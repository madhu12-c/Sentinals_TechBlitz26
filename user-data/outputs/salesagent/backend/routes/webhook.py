from fastapi import APIRouter, Form, Request
from db.mongo import create_lead, log_event
from agent.graph import start_agent
import asyncio

router = APIRouter()


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From:        str = Form(...),
    Body:        str = Form(...),
    ProfileName: str = Form(default="Unknown")
):
    """
    Twilio calls this endpoint when someone sends a WhatsApp message
    to your sandbox number. This is your primary lead capture point.
    """
    lead_data = {
        "source":  "whatsapp",
        "phone":   From,
        "name":    ProfileName,
        "message": Body.strip(),
        "email":   None
    }

    lead_id = await create_lead(lead_data)
    await log_event(lead_id, "webhook", f"Lead captured from WhatsApp: {From}")

    # Run agent in background so Twilio doesn't time out waiting
    asyncio.create_task(start_agent(lead_id, lead_data))

    # Twilio expects a TwiML response (can be empty)
    return {"status": "received", "lead_id": lead_id}


@router.post("/webhook/form")
async def form_webhook(request: Request):
    """
    Receives a lead from your website form as JSON.
    Expected body: { name, phone, email, message, source }
    """
    data = await request.json()

    lead_data = {
        "source":  data.get("source", "form"),
        "phone":   data.get("phone", ""),
        "name":    data.get("name", "Unknown"),
        "message": data.get("message", "").strip(),
        "email":   data.get("email")
    }

    lead_id = await create_lead(lead_data)
    await log_event(lead_id, "webhook", f"Lead captured from form: {lead_data['name']}")

    # Run agent in background
    asyncio.create_task(start_agent(lead_id, lead_data))

    return {"status": "received", "lead_id": lead_id}


@router.post("/webhook/rep-reply")
async def rep_reply_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Twilio calls this when the sales rep replies to the notification WhatsApp.
    Parses APPROVE or REJECT and resumes the paused LangGraph graph.
    """
    reply   = Body.strip().lower()
    lead_id = None

    # Try to extract lead_id from the reply
    # Reps can reply: "APPROVE <lead_id>" or just "APPROVE"
    # We also store the last notified lead_id in a simple in-memory store
    parts = reply.split()
    if len(parts) >= 2:
        decision = parts[0]
        lead_id  = parts[1]
    else:
        decision = parts[0] if parts else "reject"
        # Fallback: get the most recent awaiting_decision lead
        from db.mongo import get_db
        db   = get_db()
        lead = await db.leads.find_one(
            {"status": "awaiting_decision"},
            sort=[("created_at", -1)]
        )
        if lead:
            lead_id = str(lead["_id"])

    if not lead_id:
        return {"status": "error", "message": "Could not identify lead"}

    decision_clean = "approve" if decision in ("approve", "approved", "yes", "y") else "reject"

    # Resume the paused graph
    from agent.graph import resume_agent
    asyncio.create_task(resume_agent(lead_id, decision_clean))

    await log_event(lead_id, "rep_reply", f"Rep replied: {decision_clean}")

    return {"status": "ok", "decision": decision_clean, "lead_id": lead_id}
