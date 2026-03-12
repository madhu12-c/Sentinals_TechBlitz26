from agent.state import LeadState
from integrations.groq_client import research_lead_prompt
from db.mongo import update_lead, log_event


async def run(state: LeadState) -> LeadState:
    """
    Node 1 — research_lead
    Calls Claude to research the lead based on their message and details.
    Writes research_summary back to state and MongoDB.
    """
    print(f"[research_lead] Processing lead: {state['name']}")

    try:
        summary = await research_lead_prompt(
            name=state["name"],
            phone=state["phone"],
            message=state["message"],
            source=state["source"]
        )

        # Save to MongoDB
        await update_lead(state["lead_id"], {
            "research_summary": summary,
            "status": "researching"
        })

        await log_event(
            lead_id=state["lead_id"],
            node="research_lead",
            description=f"Lead researched: {summary[:80]}..."
        )

        print(f"[research_lead] Done. Summary: {summary[:60]}...")
        return {**state, "research_summary": summary}

    except Exception as e:
        error_msg = f"research_lead failed: {str(e)}"
        print(f"[research_lead] ERROR: {error_msg}")
        await log_event(state["lead_id"], "research_lead", f"ERROR: {error_msg}")
        return {**state, "research_summary": "Research unavailable.", "error": error_msg}
