from agent.state import LeadState
from integrations.groq_client import score_lead_prompt
from db.mongo import update_lead, log_event, get_company, get_latest_insights


async def run(state: LeadState) -> LeadState:
    """
    Node 2 — score_lead
    Calls Claude to score the lead 1-10, get a reason, and a suggested message.
    Uses company context, detected language, and past performance insights.
    """
    print(f"[score_lead] Scoring lead: {state['name']}")

    try:
        # Step 1: Get company context
        company = await get_company()
        context = f"{company['name']}: {company['description']} targeting {company['target_audience']}"

        # Step 2: Get scoring insights from past performance
        insights_doc = await get_latest_insights()
        scoring_tips = insights_doc.get("text", "") if insights_doc else ""

        # Step 3: Score lead
        result = await score_lead_prompt(
            name=state["name"],
            message=state["message"],
            source=state["source"],
            research_summary=state.get("research_summary", "No research available."),
            language=state.get("language", "English"),
            company_context=context,
            scoring_tips=scoring_tips
        )

        score           = result.get("score", 5)
        score_reason    = result.get("reason", "No reason provided.")
        suggested_msg   = result.get("suggested_message", "")

        # Save to MongoDB
        await update_lead(state["lead_id"], {
            "score": score,
            "score_reason": score_reason,
            "suggested_message": suggested_msg,
            "status": "scored"
        })

        await log_event(
            lead_id=state["lead_id"],
            node="score_lead",
            description=f"Language: {state.get('language')}. Lead scored {score}/10 — {score_reason[:80]}"
        )

        print(f"[score_lead] Score: {score}/10")
        return {
            **state,
            "score": score,
            "score_reason": score_reason,
            "suggested_message": suggested_msg
        }

    except Exception as e:
        error_msg = f"score_lead failed: {str(e)}"
        print(f"[score_lead] ERROR: {error_msg}")
        await log_event(state["lead_id"], "score_lead", f"ERROR: {error_msg}")
        return {**state, "score": 5, "score_reason": "Scoring failed.", "error": error_msg}
