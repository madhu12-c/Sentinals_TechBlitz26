from agent.state import LeadState
from db.mongo import update_lead, log_event


async def run(state: LeadState) -> LeadState:
    """
    Node 5 — archive_lead
    Called when the rep rejects a lead.
    Updates status to 'rejected' in MongoDB and logs the event.
    """
    print(f"[archive_lead] Archiving rejected lead: {state['name']}")

    await update_lead(state["lead_id"], {"status": "rejected"})

    await log_event(
        lead_id=state["lead_id"],
        node="archive_lead",
        description=f"Lead rejected and archived by rep."
    )

    print(f"[archive_lead] Lead {state['lead_id']} archived.")
    return {**state}
