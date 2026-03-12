from agent.state import LeadState
from db.mongo import update_lead, log_event
from scheduler.jobs import schedule_followup


async def run(state: LeadState) -> LeadState:
    """
    Node 6 — follow_up
    Schedules automatic follow-up jobs via APScheduler.
    If no reply from the lead, the scheduler fires follow-up messages.
    Max 3 follow-ups before marking lead as cold.
    """
    print(f"[follow_up] Scheduling follow-up for: {state['name']}")

    follow_up_count = state.get("follow_up_count", 0)
    MAX_FOLLOWUPS   = 3

    if follow_up_count >= MAX_FOLLOWUPS:
        # Lead has gone cold after max follow-ups
        await update_lead(state["lead_id"], {"status": "cold"})
        await log_event(
            lead_id=state["lead_id"],
            node="follow_up",
            description=f"Lead marked cold after {MAX_FOLLOWUPS} follow-ups with no reply."
        )
        print(f"[follow_up] Lead cold after {MAX_FOLLOWUPS} attempts.")
        return {**state}

    # Schedule the next follow-up job
    schedule_followup(
        lead_id=state["lead_id"],
        name=state["name"],
        phone=state.get("phone", ""),
        email=state.get("email"),
        follow_up_count=follow_up_count + 1
    )

    await update_lead(state["lead_id"], {
        "status": "follow_up",
        "follow_up_count": follow_up_count + 1
    })

    await log_event(
        lead_id=state["lead_id"],
        node="follow_up",
        description=f"Follow-up #{follow_up_count + 1} scheduled."
    )

    print(f"[follow_up] Follow-up #{follow_up_count + 1} scheduled for {state['name']}")
    return {**state, "follow_up_count": follow_up_count + 1}
