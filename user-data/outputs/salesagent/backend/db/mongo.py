from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING
from datetime import datetime, timezone
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

# ── Connection singleton ───────────────────────────────────────────────────────
client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client["salesagent"]
    print("[OK] MongoDB connected")


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db


# ── Lead helpers ───────────────────────────────────────────────────────────────
async def create_lead(data: dict) -> str:
    """Insert a new lead, return its string id."""
    data["created_at"] = datetime.now(timezone.utc)
    data["updated_at"] = datetime.now(timezone.utc)
    data["status"] = "new"
    data["outreach_sent"] = False
    data["follow_up_count"] = 0
    result = await db.leads.insert_one(data)
    return str(result.inserted_id)


async def get_lead(lead_id: str) -> dict:
    doc = await db.leads.find_one({"_id": ObjectId(lead_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def update_lead(lead_id: str, updates: dict):
    updates["updated_at"] = datetime.now(timezone.utc)
    await db.leads.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": updates}
    )


async def get_all_leads(limit: int = 50) -> list:
    cursor = db.leads.find().sort("created_at", DESCENDING).limit(limit)
    leads = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        leads.append(doc)
    return leads


# ── Agent event helpers ────────────────────────────────────────────────────────
async def log_event(lead_id: str, node: str, description: str, channel: str = None):
    """Log an agent action to the agent_events collection."""
    event = {
        "lead_id": lead_id,
        "node": node,
        "description": description,
        "channel": channel,
        "timestamp": datetime.now(timezone.utc)
    }
    await db.agent_events.insert_one(event)


async def get_events(lead_id: str = None, limit: int = 30) -> list:
    query = {"lead_id": lead_id} if lead_id else {}
    cursor = db.agent_events.find(query).sort("timestamp", DESCENDING).limit(limit)
    events = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    return events


# ── Thread ID helpers (for LangGraph resume) ──────────────────────────────────
async def save_thread_id(lead_id: str, thread_id: str):
    await update_lead(lead_id, {"thread_id": thread_id})


async def get_thread_id(lead_id: str) -> str:
    doc = await get_lead(lead_id)
    return doc.get("thread_id") if doc else None
