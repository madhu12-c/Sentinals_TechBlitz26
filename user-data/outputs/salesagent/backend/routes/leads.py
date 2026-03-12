from fastapi import APIRouter, HTTPException
from db.mongo import get_all_leads, get_lead, update_lead, get_events, log_event
from agent.graph import resume_agent
import asyncio

router = APIRouter()


@router.get("/leads")
async def list_leads(limit: int = 50):
    """Return all leads sorted by most recent. Used by dashboard."""
    leads = await get_all_leads(limit=limit)
    return {"leads": leads, "count": len(leads)}


@router.get("/leads/metrics")
async def get_metrics():
    """Return KPI counts for dashboard metric cards."""
    from db.mongo import get_db
    db = get_db()

    total      = await db.leads.count_documents({})
    awaiting   = await db.leads.count_documents({"status": "awaiting_decision"})
    approved   = await db.leads.count_documents({"status": {"$in": ["contacted", "follow_up", "converted"]}})
    converted  = await db.leads.count_documents({"status": "converted"})

    return {
        "total":     total,
        "awaiting":  awaiting,
        "approved":  approved,
        "converted": converted
    }


@router.get("/leads/{lead_id}")
async def get_lead_detail(lead_id: str):
    """Return full detail for a single lead. Used by LeadDetail page."""
    lead = await get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/leads/{lead_id}/decide")
async def decide_on_lead(lead_id: str, body: dict):
    """
    Called from the React UI approve/reject buttons.
    Resumes the paused LangGraph graph with the decision.
    Body: { "decision": "approve" | "reject" }
    """
    decision = body.get("decision", "reject").lower()
    if decision not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Decision must be 'approve' or 'reject'")

    lead = await get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    await log_event(lead_id, "ui_decision", f"Decision from UI: {decision}")
    asyncio.create_task(resume_agent(lead_id, decision))

    return {"status": "ok", "decision": decision, "lead_id": lead_id}


@router.get("/events")
async def list_events(lead_id: str = None, limit: int = 30):
    """Return agent events. Used by dashboard activity log."""
    events = await get_events(lead_id=lead_id, limit=limit)
    return {"events": events}


@router.post("/leads/{lead_id}/convert")
async def mark_converted(lead_id: str):
    """Mark a lead as converted when they become a customer."""
    await update_lead(lead_id, {"status": "converted"})
    await log_event(lead_id, "convert", "Lead manually marked as converted.")
    return {"status": "ok"}
