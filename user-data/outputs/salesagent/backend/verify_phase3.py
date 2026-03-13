import asyncio
import os
import sys
from bson import ObjectId

# Add the project root to sys.path
sys.path.append(os.getcwd())

from db.mongo import connect_db, get_db, log_outcome, close_db
from agent.nodes.learn import trigger_learning_if_needed

async def mock_outcomes():
    await connect_db()
    db = get_db()
    
    print("[test] Cleaning up previous test data...")
    await db.lead_outcomes.delete_many({})
    await db.learning_stats.delete_many({})
    await db.company_insights.delete_many({})
    
    print("[test] Creating a dummy lead...")
    # Use a real ObjectId for the test
    lead_oid = ObjectId()
    lead_id = str(lead_oid)
    
    await db.leads.insert_one({
        "_id": lead_oid,
        "name": "Test User",
        "source": "whatsapp",
        "message": "I want to buy a bike",
        "score": 8,
        "research_summary": "High intent buyer."
    })

    print(f"[test] Mocking 10 outcomes for lead {lead_id}...")
    for i in range(10):
        outcome = "won" if i % 3 == 0 else "lost"
        # Since log_outcome calls get_lead(lead_id) and expects lead_id as a string
        await log_outcome(lead_id, outcome)
        print(f"  Logged outcome {i+1}/10: {outcome}")
    
    print("[test] Triggering learning...")
    await trigger_learning_if_needed()
    
    insights = await db.company_insights.find_one({})
    if insights:
        print("\n[SUCCESS] AI Insights generated:")
        print(f"--- TEXT ---\n{insights['text']}\n------------")
    else:
        # Check if maybe they were inserted but find_one failed
        count = await db.company_insights.count_documents({})
        print(f"\n[DEBUG] Insights count: {count}")

    await close_db()

if __name__ == "__main__":
    asyncio.run(mock_outcomes())
