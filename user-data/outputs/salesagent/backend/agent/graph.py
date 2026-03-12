from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agent.state import LeadState
from agent.nodes import research, score, notify, outreach, archive, followup, log_db

# ── Memory checkpointer ────────────────────────────────────────────────────────
# MemorySaver keeps graph state in RAM.
# This is what allows interrupt() to pause and resume correctly.
# For production, swap with a Redis or PostgreSQL checkpointer.
memory = MemorySaver()


def route_decision(state: LeadState) -> str:
    """
    Conditional edge function.
    Called after notify_rep to decide which branch to take.
    Returns "approved" or "rejected".
    """
    decision = state.get("rep_decision", "reject").strip().lower()
    if decision in ("approve", "approved", "yes", "y"):
        return "approved"
    return "rejected"


def build_graph():
    """
    Build and compile the LangGraph StateGraph.
    Returns a compiled graph ready to invoke.

    Graph flow:
    research_lead
        -> score_lead
            -> notify_rep  [interrupt() — waits for rep]
                -> [approve] -> send_outreach -> follow_up -> log_to_db -> END
                -> [reject]  -> archive_lead -> log_to_db  -> END
    """
    g = StateGraph(LeadState)

    # ── Add all nodes ──────────────────────────────────────────────────
    g.add_node("research_lead", research.run)
    g.add_node("score_lead",    score.run)
    g.add_node("notify_rep",    notify.run)
    g.add_node("send_outreach", outreach.run)
    g.add_node("archive_lead",  archive.run)
    g.add_node("follow_up",     followup.run)
    g.add_node("log_to_db",     log_db.run)

    # ── Set entry point ────────────────────────────────────────────────
    g.set_entry_point("research_lead")

    # ── Add sequential edges ───────────────────────────────────────────
    g.add_edge("research_lead", "score_lead")
    g.add_edge("score_lead",    "notify_rep")

    # ── Conditional branch after rep decision ──────────────────────────
    g.add_conditional_edges(
        "notify_rep",
        route_decision,
        {
            "approved": "send_outreach",
            "rejected": "archive_lead"
        }
    )

    # ── Outreach path ──────────────────────────────────────────────────
    g.add_edge("send_outreach", "follow_up")
    g.add_edge("follow_up",     "log_to_db")

    # ── Archive path ───────────────────────────────────────────────────
    g.add_edge("archive_lead",  "log_to_db")

    # ── Final node ─────────────────────────────────────────────────────
    g.add_edge("log_to_db", END)

    # ── Compile with checkpointer ──────────────────────────────────────
    # interrupt_before=["notify_rep"] tells LangGraph to pause
    # BEFORE executing notify_rep so we can inject the rep's decision.
    compiled = g.compile(
        checkpointer=memory,
        interrupt_before=["notify_rep"]
    )

    return compiled


# ── Singleton instance ─────────────────────────────────────────────────────────
graph = build_graph()


async def start_agent(lead_id: str, lead_data: dict) -> dict:
    """
    Start the agent for a new lead.
    Runs research -> score -> then pauses before notify_rep.
    Returns the graph state after scoring.
    """
    import uuid
    thread_id = str(uuid.uuid4())

    # Save thread_id so we can resume later
    from db.mongo import save_thread_id
    await save_thread_id(lead_id, thread_id)

    initial_state: LeadState = {
        "lead_id":          lead_id,
        "source":           lead_data.get("source", "unknown"),
        "name":             lead_data.get("name", "Unknown"),
        "phone":            lead_data.get("phone", ""),
        "message":          lead_data.get("message", ""),
        "email":            lead_data.get("email"),
        "research_summary": None,
        "score":            None,
        "score_reason":     None,
        "suggested_message": None,
        "rep_decision":     None,
        "outreach_sent":    False,
        "follow_up_count":  0,
        "error":            None
    }

    config = {"configurable": {"thread_id": thread_id}}

    # Run until interrupt (before notify_rep)
    state = await graph.ainvoke(initial_state, config=config)

    # Now manually trigger the notify step
    await graph.ainvoke(None, config=config)

    return {"thread_id": thread_id, "state": state}


async def resume_agent(lead_id: str, decision: str) -> dict:
    """
    Resume a paused graph with the rep's decision.
    Called by the WhatsApp webhook when rep replies APPROVE or REJECT.
    """
    from db.mongo import get_thread_id
    thread_id = await get_thread_id(lead_id)

    if not thread_id:
        raise ValueError(f"No thread_id found for lead {lead_id}")

    config = {"configurable": {"thread_id": thread_id}}

    # Resume with the rep's decision
    state = await graph.ainvoke(
        {"rep_decision": decision},
        config=config
    )

    return {"thread_id": thread_id, "state": state}
