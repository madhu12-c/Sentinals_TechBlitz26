from db.mongo import get_recent_outcomes, save_insights, log_event, get_db
from integrations.groq_client import generate_scoring_insights
from datetime import datetime, timezone

async def trigger_learning_if_needed():
    """
    Check if we have enough new outcomes to trigger a learning session.
    A session is triggered every 10 outcomes.
    """
    db = get_db()
    
    # Get total outcomes count
    total_outcomes = await db.lead_outcomes.count_documents({})
    
    # Simple logic: check if we've learned since the last 10 outcomes
    # We store the last learned count in a small config collection
    stats = await db.learning_stats.find_one({"id": "learning_progress"})
    last_count = stats.get("last_learned_at", 0) if stats else 0
    
    if total_outcomes >= last_count + 10:
        print(f"[learn] Triggering learning session. New outcomes: {total_outcomes - last_count}")
        
        # 1. Fetch recent outcomes
        outcomes = await get_recent_outcomes(limit=50)
        
        # 2. Generate insights using Groq
        try:
            insights_text = await generate_scoring_insights(outcomes)
            
            # 3. Save insights
            await save_insights(insights_text)
            
            # 4. Update stats
            await db.learning_stats.update_one(
                {"id": "learning_progress"},
                {"$set": {"last_learned_at": total_outcomes, "updated_at": datetime.now(timezone.utc)}},
                upsert=True
            )
            
            await log_event(
                lead_id="system",
                node="learning_node",
                description="AI Agent successfully learned from recent outcomes and generated new scoring tips."
            )
            print("[learn] Learning completed and insights saved.")
            
        except Exception as e:
            print(f"[learn] Error during learning: {str(e)}")
            await log_event("system", "learning_node", f"ERROR during learning: {str(e)}")
    else:
        print(f"[learn] Not enough new outcomes yet ({total_outcomes - last_count}/10)")
