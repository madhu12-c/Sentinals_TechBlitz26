from agent.state import LeadState
from db.mongo import update_lead, log_event
from datetime import datetime, timezone


async def run(state: LeadState) -> LeadState:
    """
    Node 7 — log_to_db
    Final node. Saves the complete agent run summary to MongoDB.
    Both approve and reject paths converge here.
    """
    print(f"[log_to_db] Saving final state for lead: {state['name']}")

    summary = {
        "agent_completed_at": datetime.now(timezone.utc),
        "final_score": state.get("score"),
        "final_status": "contacted" if state.get("outreach_sent") else "rejected",
        "outreach_sent": state.get("outreach_sent", False),
        "follow_up_count": state.get("follow_up_count", 0),
    }

    await update_lead(state["lead_id"], summary)

    await log_event(
        lead_id=state["lead_id"],
        node="log_to_db",
        description=f"Agent run complete. Score: {state.get('score')}/10. Outreach sent: {state.get('outreach_sent', False)}."
    )

    print(f"[log_to_db] Agent run complete for lead: {state['lead_id']}")
    return {**state}
