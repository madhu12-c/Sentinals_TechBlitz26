from agent.state import LeadState
from integrations.groq_client import research_lead_prompt, detect_language
from db.mongo import update_lead, log_event, get_company


async def run(state: LeadState) -> LeadState:
    """
    Node 1 — research_lead
    Detects language and calls Claude to research the lead.
    """
    print(f"[research_lead] Processing lead: {state['name']}")

    try:
        # Step 1: Detect language
        lang = await detect_language(state["message"])
        print(f"[research_lead] Detected language: {lang}")

        # Step 2: Get company context
        company = await get_company()
        context = f"{company['name']}: {company['description']} targeting {company['target_audience']}"

        # Step 3: Research in detected language
        summary = await research_lead_prompt(
            name=state["name"],
            phone=state["phone"],
            message=state["message"],
            source=state["source"],
            language=lang,
            company_context=context
        )

        # Update DB
        await update_lead(state["lead_id"], {
            "language": lang,
            "research_summary": summary,
            "status": "researching"
        })

        await log_event(
            lead_id=state["lead_id"],
            node="research_lead",
            description=f"Language: {lang}. Lead researched: {summary[:80]}..."
        )

        return {**state, "language": lang, "research_summary": summary}

    except Exception as e:
        error_msg = f"research_lead failed: {str(e)}"
        print(f"[research_lead] ERROR: {error_msg}")
        await log_event(state["lead_id"], "research_lead", f"ERROR: {error_msg}")
        return {**state, "research_summary": "Research unavailable.", "error": error_msg}
