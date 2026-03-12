"""
SalesAgent Backend — Test Script
Tests each component individually, then tests the full pipeline.
Run with: python test_agents.py
"""
import asyncio
import os
import sys
import json
from datetime import datetime, timezone

# Ensure dotenv is loaded
from dotenv import load_dotenv
load_dotenv()

# ── Colour helpers for test output ─────────────────────────────────────────────
PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"
INFO = "[INFO]"

results = []

def log_result(test_name: str, passed: bool, detail: str = ""):
    status = PASS if passed else FAIL
    results.append((test_name, passed, detail))
    print(f"  {status} {test_name}" + (f" -- {detail}" if detail else ""))


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: MongoDB Connection
# ═══════════════════════════════════════════════════════════════════════════════
async def test_mongodb():
    print("\n--- Test 1: MongoDB Connection ---")
    try:
        from db.mongo import connect_db, close_db, get_db
        await connect_db()
        db = get_db()
        # Ping the database
        result = await db.command("ping")
        log_result("MongoDB connect", True, f"ping response: {result}")

        # Test CRUD operations
        test_doc = {"_test": True, "created_at": datetime.now(timezone.utc)}
        insert_result = await db.test_collection.insert_one(test_doc)
        log_result("MongoDB insert", bool(insert_result.inserted_id),
                   f"inserted_id: {insert_result.inserted_id}")

        # Read back
        found = await db.test_collection.find_one({"_id": insert_result.inserted_id})
        log_result("MongoDB read", found is not None)

        # Cleanup
        await db.test_collection.delete_one({"_id": insert_result.inserted_id})
        log_result("MongoDB cleanup", True)

        await close_db()
        return True
    except Exception as e:
        log_result("MongoDB connect", False, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: Claude Client (Research + Score)
# ═══════════════════════════════════════════════════════════════════════════════
async def test_groq():
    print("\n--- Test 2: Groq Client (AI) ---")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your-groq-api-key-here":
        log_result("Groq API key present", False, "GROQ_API_KEY not set in .env")
        return False

    log_result("Groq API key present", True, f"key starts with: {api_key[:12]}...")

    try:
        from integrations.groq_client import research_lead_prompt, score_lead_prompt

        # Test research
        print(f"  {INFO} Calling Groq for lead research (this may take a few seconds)...")
        summary = await research_lead_prompt(
            name="Test User",
            phone="+910000000000",
            message="I want to buy 50 licenses of your software for my team",
            source="form"
        )
        log_result("Groq research_lead", bool(summary and len(summary) > 10),
                   f"response length: {len(summary)} chars")
        print(f"  {INFO} Research summary: {summary[:100]}...")

        # Test scoring
        print(f"  {INFO} Calling Groq for lead scoring...")
        score_result = await score_lead_prompt(
            name="Test User",
            message="I want to buy 50 licenses of your software for my team",
            source="form",
            research_summary=summary
        )
        has_score = isinstance(score_result.get("score"), int)
        has_reason = bool(score_result.get("reason"))
        has_msg = bool(score_result.get("suggested_message"))
        log_result("Groq score_lead", has_score and has_reason,
                   f"score={score_result.get('score')}/10")
        log_result("Groq suggested_message", has_msg,
                   f"length: {len(score_result.get('suggested_message', ''))} chars")

        return True
    except Exception as e:
        log_result("Groq API call", False, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: Twilio Client (WhatsApp)
# ═══════════════════════════════════════════════════════════════════════════════
def test_twilio():
    print("\n--- Test 3: Twilio Configuration ---")

    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_num = os.getenv("TWILIO_WHATSAPP_FROM")
    rep_num = os.getenv("REP_WHATSAPP_NUMBER")

    log_result("Twilio ACCOUNT_SID set", bool(sid), f"starts with: {sid[:8]}..." if sid else "missing")
    log_result("Twilio AUTH_TOKEN set", bool(token), "present" if token else "missing")
    log_result("Twilio WHATSAPP_FROM set", bool(from_num), from_num or "missing")
    log_result("Twilio REP_NUMBER set", bool(rep_num), rep_num or "missing")

    try:
        from integrations.twilio_client import twilio_client
        # Just verify the client object exists (we won't send a real message)
        log_result("Twilio client init", True, "client object created")
        return True
    except Exception as e:
        log_result("Twilio client init", False, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: SendGrid Client (Email)
# ═══════════════════════════════════════════════════════════════════════════════
def test_sendgrid():
    print("\n--- Test 4: SendGrid Configuration ---")

    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL")

    log_result("SendGrid API key set", bool(api_key),
               f"starts with: {api_key[:10]}..." if api_key else "missing")
    log_result("SendGrid FROM_EMAIL set", bool(from_email), from_email or "missing")

    try:
        from integrations.sendgrid_client import sg_client
        log_result("SendGrid client init", True, "client object created")
        return True
    except Exception as e:
        log_result("SendGrid client init", False, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: LangGraph Agent (Graph Build + State)
# ═══════════════════════════════════════════════════════════════════════════════
def test_langgraph():
    print("\n--- Test 5: LangGraph Agent Graph ---")

    try:
        from langgraph.types import interrupt
        log_result("langgraph.types.interrupt import", True)
    except ImportError as e:
        log_result("langgraph.types.interrupt import", False, str(e))
        return False

    try:
        from langgraph.graph import StateGraph, END
        from langgraph.checkpoint.memory import MemorySaver
        log_result("langgraph core imports", True)
    except ImportError as e:
        log_result("langgraph core imports", False, str(e))
        return False

    try:
        from agent.state import LeadState
        log_result("LeadState import", True)
    except ImportError as e:
        log_result("LeadState import", False, str(e))
        return False

    try:
        from agent.graph import build_graph, graph
        log_result("build_graph() success", True, f"graph type: {type(graph).__name__}")
    except Exception as e:
        log_result("build_graph()", False, str(e))
        return False

    # Verify graph has expected nodes
    try:
        nodes = list(graph.nodes.keys()) if hasattr(graph, 'nodes') else []
        expected = ["research_lead", "score_lead", "notify_rep",
                    "send_outreach", "archive_lead", "follow_up", "log_to_db"]
        all_present = all(n in nodes for n in expected)
        log_result("Graph has all 7 nodes", all_present,
                   f"found: {nodes}")
    except Exception as e:
        log_result("Graph node check", False, str(e))

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 6: Agent Nodes (import check)
# ═══════════════════════════════════════════════════════════════════════════════
def test_node_imports():
    print("\n--- Test 6: Agent Node Imports ---")
    nodes = ["research", "score", "notify", "outreach", "archive", "followup", "log_db"]
    all_ok = True
    for node_name in nodes:
        try:
            mod = __import__(f"agent.nodes.{node_name}", fromlist=["run"])
            has_run = hasattr(mod, "run") and callable(mod.run)
            log_result(f"Node '{node_name}' import", has_run,
                       "has run() function" if has_run else "missing run()")
            if not has_run:
                all_ok = False
        except Exception as e:
            log_result(f"Node '{node_name}' import", False, str(e))
            all_ok = False
    return all_ok


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 7: API Endpoints (requires running server)
# ═══════════════════════════════════════════════════════════════════════════════
async def test_api_endpoints():
    print("\n--- Test 7: API Endpoints (server must be running on :8000) ---")
    import httpx

    try:
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=5.0) as client:
            # Health check
            r = await client.get("/health")
            log_result("GET /health", r.status_code == 200, f"status={r.status_code}")

            # Root
            r = await client.get("/")
            log_result("GET /", r.status_code == 200, f"response: {r.json()}")

            # Leads list
            r = await client.get("/leads")
            log_result("GET /leads", r.status_code == 200,
                       f"count: {r.json().get('count', '?')}")

            # Metrics
            r = await client.get("/leads/metrics")
            log_result("GET /leads/metrics", r.status_code == 200,
                       f"data: {r.json()}")

            # Events
            r = await client.get("/events")
            log_result("GET /events", r.status_code == 200,
                       f"events count: {len(r.json().get('events', []))}")

            return True

    except httpx.ConnectError:
        log_result("API server reachable", False,
                   "Cannot connect to localhost:8000. Is the server running?")
        return False
    except Exception as e:
        log_result("API endpoints", False, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 8: Full Pipeline (submit a lead through the form webhook)
# ═══════════════════════════════════════════════════════════════════════════════
async def test_full_pipeline():
    print("\n--- Test 8: Full Pipeline (submit lead via /webhook/form) ---")
    import httpx

    try:
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
            # Submit a test lead
            payload = {
                "name": "Test Lead from Agents Test",
                "phone": "+910000000000",
                "email": "test@example.com",
                "message": "Testing the agent pipeline end to end -- please ignore",
                "source": "test"
            }

            print(f"  {INFO} Submitting test lead via /webhook/form...")
            r = await client.post("/webhook/form", json=payload)
            log_result("POST /webhook/form", r.status_code == 200,
                       f"status={r.status_code}, response={r.json()}")

            if r.status_code != 200:
                return False

            lead_id = r.json().get("lead_id")
            log_result("Lead ID returned", bool(lead_id), f"lead_id={lead_id}")

            if not lead_id:
                return False

            # Wait for the agent pipeline to process
            print(f"  {INFO} Waiting 15 seconds for agent pipeline to process...")
            await asyncio.sleep(15)

            # Check the lead status
            r = await client.get(f"/leads/{lead_id}")
            if r.status_code == 200:
                lead = r.json()
                status = lead.get("status", "unknown")
                score = lead.get("score")
                research = lead.get("research_summary")
                log_result("Lead has research_summary", bool(research),
                           f"length: {len(research) if research else 0} chars")
                log_result("Lead has score", score is not None,
                           f"score: {score}/10" if score else "no score")
                log_result("Lead status progressed", status != "new",
                           f"status: {status}")
            else:
                log_result("Lead detail fetch", False, f"status={r.status_code}")

            # Check agent events for this lead
            r = await client.get(f"/events?lead_id={lead_id}")
            if r.status_code == 200:
                events = r.json().get("events", [])
                log_result("Agent events logged", len(events) > 0,
                           f"{len(events)} events recorded")
                for ev in events:
                    print(f"    -> [{ev.get('node')}] {ev.get('description', '')[:80]}")
            else:
                log_result("Events fetch", False, f"status={r.status_code}")

            return True

    except httpx.ConnectError:
        log_result("API server reachable", False,
                   "Cannot connect to localhost:8000. Is the server running?")
        return False
    except Exception as e:
        log_result("Full pipeline", False, str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
async def main():
    print("=" * 60)
    print("  SalesAgent Backend -- Test Suite")
    print("=" * 60)

    # Tests that don't need a running server
    db_ok = await test_mongodb()
    groq_ok = await test_groq()
    twilio_ok = test_twilio()
    sendgrid_ok = test_sendgrid()
    graph_ok = test_langgraph()
    nodes_ok = test_node_imports()

    # Tests that need the server running
    api_ok = await test_api_endpoints()

    # Full pipeline test (only if server and deps are OK)
    if api_ok and db_ok and groq_ok:
        pipeline_ok = await test_full_pipeline()
    else:
        print(f"\n--- Test 8: Full Pipeline ---")
        print(f"  {SKIP} Skipping full pipeline (requires server + DB + Groq)")
        pipeline_ok = False

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, p, _ in results if p)
    failed = sum(1 for _, p, _ in results if not p)

    for name, ok, detail in results:
        status = PASS if ok else FAIL
        print(f"  {status} {name}")

    print(f"\n  Total: {len(results)} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("\n  All tests passed!")
    else:
        print(f"\n  {failed} test(s) failed -- see details above.")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
