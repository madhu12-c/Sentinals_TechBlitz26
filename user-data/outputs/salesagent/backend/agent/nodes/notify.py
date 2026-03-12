from langgraph.types import interrupt
from agent.state import LeadState
from integrations.twilio_client import notify_rep as send_rep_whatsapp
from db.mongo import update_lead, log_event


async def run(state: LeadState) -> LeadState:
    """
    Node 3 — notify_rep
    Sends a WhatsApp message to the sales rep with the lead score.
    Then calls interrupt() to PAUSE the graph and wait for the rep's reply.
    The graph resumes when FastAPI receives the rep's WhatsApp reply.
    """
    print(f"[notify_rep] Notifying rep about: {state['name']} (score: {state.get('score', '?')}/10)")

    try:
        # Send WhatsApp to rep
        sid = send_rep_whatsapp(
            lead_id=state["lead_id"],
            name=state["name"],
            score=state.get("score", 0),
            reason=state.get("score_reason", "No reason available."),
            source=state["source"]
        )

        await update_lead(state["lead_id"], {"status": "awaiting_decision"})

        await log_event(
            lead_id=state["lead_id"],
            node="notify_rep",
            description=f"Rep notified via WhatsApp (score {state.get('score')}/10). SID: {sid}",
            channel="whatsapp"
        )

        print(f"[notify_rep] WhatsApp sent to rep. Message SID: {sid}")
        print(f"[notify_rep] Graph pausing — waiting for rep decision...")

        # ── HUMAN IN THE LOOP ─────────────────────────────────────────
        # This pauses the graph here until graph.invoke() is called
        # again with the rep's decision from the webhook.
        rep_decision = interrupt({
            "lead_id": state["lead_id"],
            "waiting_for": "rep_decision",
            "message": "Waiting for rep to reply APPROVE or REJECT on WhatsApp"
        })
        # ──────────────────────────────────────────────────────────────

        decision = str(rep_decision).strip().lower()
        print(f"[notify_rep] Rep decision received: {decision}")

        await update_lead(state["lead_id"], {"rep_decision": decision})
        await log_event(
            lead_id=state["lead_id"],
            node="notify_rep",
            description=f"Rep decision: {decision}"
        )

        return {**state, "rep_decision": decision}

    except Exception as e:
        error_msg = f"notify_rep failed: {str(e)}"
        print(f"[notify_rep] ERROR: {error_msg}")
        await log_event(state["lead_id"], "notify_rep", f"ERROR: {error_msg}")
        return {**state, "rep_decision": "reject", "error": error_msg}
