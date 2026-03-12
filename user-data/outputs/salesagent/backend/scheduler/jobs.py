from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone
import os

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.start()
    print("[OK] APScheduler started")


def stop_scheduler():
    scheduler.shutdown()


def schedule_followup(lead_id: str, name: str, phone: str, email: str, follow_up_count: int):
    """Schedule a follow-up job for a lead after FOLLOWUP_DELAY_MINUTES."""
    delay_minutes = int(os.getenv("FOLLOWUP_DELAY_MINUTES", 2))
    run_time      = datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)
    job_id        = f"followup_{lead_id}_{follow_up_count}"

    scheduler.add_job(
        func=execute_followup,
        trigger="date",
        run_date=run_time,
        id=job_id,
        kwargs={
            "lead_id":        lead_id,
            "name":           name,
            "phone":          phone,
            "email":          email,
            "follow_up_count": follow_up_count
        },
        replace_existing=True
    )
    print(f"[scheduler] Follow-up #{follow_up_count} for {name} scheduled at {run_time}")


async def execute_followup(lead_id: str, name: str, phone: str, email: str, follow_up_count: int):
    """
    Fired by APScheduler after the delay.
    Checks if lead has replied. If not, sends follow-up messages.
    """
    from db.mongo import get_lead, update_lead, log_event
    from integrations.twilio_client import send_lead_whatsapp
    from integrations.sendgrid_client import send_followup_email

    print(f"[scheduler] Executing follow-up #{follow_up_count} for lead {lead_id}")

    lead = await get_lead(lead_id)
    if not lead:
        print(f"[scheduler] Lead {lead_id} not found. Skipping.")
        return

    # If lead already converted or cold, skip
    if lead.get("status") in ("converted", "cold", "rejected"):
        print(f"[scheduler] Lead {lead_id} status is '{lead['status']}'. Skipping follow-up.")
        return

    channels_used = []

    # Send WhatsApp follow-up
    if phone:
        followup_messages = [
            f"Hi {name}! Just checking in — did you get a chance to see my last message? Happy to answer any questions. 😊",
            f"Hey {name}, following up once more. We'd love to help — let us know if you're still interested!",
            f"Hi {name}, this is my last follow-up. If timing isn't right, no worries at all. Feel free to reach out anytime!"
        ]
        idx = min(follow_up_count - 1, len(followup_messages) - 1)
        try:
            send_lead_whatsapp(to=phone, message=followup_messages[idx])
            channels_used.append("whatsapp")
        except Exception as e:
            print(f"[scheduler] WhatsApp follow-up failed: {e}")

    # Send email follow-up
    if email:
        try:
            send_followup_email(name=name, to_email=email, follow_up_count=follow_up_count)
            channels_used.append("email")
        except Exception as e:
            print(f"[scheduler] Email follow-up failed: {e}")

    # Update MongoDB
    new_count = follow_up_count
    status    = "cold" if follow_up_count >= 3 else "follow_up"
    await update_lead(lead_id, {"follow_up_count": new_count, "status": status})
    await log_event(
        lead_id=lead_id,
        node="follow_up",
        description=f"Follow-up #{follow_up_count} sent via {', '.join(channels_used) if channels_used else 'no channels'}.",
        channel=",".join(channels_used)
    )

    # Schedule next follow-up if not at max
    if follow_up_count < 3:
        schedule_followup(
            lead_id=lead_id,
            name=name,
            phone=phone,
            email=email,
            follow_up_count=follow_up_count + 1
        )
