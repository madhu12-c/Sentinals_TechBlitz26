from agent.state import LeadState
from integrations.twilio_client import send_lead_whatsapp, make_voice_call
from integrations.sendgrid_client import send_outreach_email
from db.mongo import update_lead, log_event


async def run(state: LeadState) -> LeadState:
    """
    Node 4 — send_outreach
    Sends personalised outreach to the approved lead across:
    - Email (SendGrid)
    - WhatsApp (Twilio)
    - Voice call (Twilio) — only for high-score leads (8+)
    """
    print(f"[send_outreach] Sending outreach to: {state['name']}")

    suggested_msg = state.get("suggested_message", "")
    phone         = state.get("phone", "")
    score         = state.get("score", 0)
    channels_used = []

    # ── 1. Email outreach ─────────────────────────────────────────────
    # Note: email requires the lead to have provided their email.
    # For WhatsApp leads we fall back to WA only.
    email = state.get("email")
    if email:
        success = send_outreach_email(
            name=state["name"],
            to_email=email,
            suggested_message=suggested_msg
        )
        if success:
            channels_used.append("email")
            await log_event(
                lead_id=state["lead_id"],
                node="send_outreach",
                description=f"Email sent to {email}",
                channel="email"
            )

    # ── 2. WhatsApp outreach ──────────────────────────────────────────
    if phone:
        try:
            send_lead_whatsapp(to=phone, message=suggested_msg)
            channels_used.append("whatsapp")
            await log_event(
                lead_id=state["lead_id"],
                node="send_outreach",
                description=f"WhatsApp sent to {phone}",
                channel="whatsapp"
            )
        except Exception as e:
            print(f"[send_outreach] WhatsApp failed: {e}")

    # ── 3. Voice call for high-score leads ────────────────────────────
    if score >= 8 and phone:
        try:
            voice_script = (
                f"Hello, this is a message for {state['name']}. "
                f"Thank you for your interest. One of our team members will "
                f"be in touch with you very shortly. Have a great day!"
            )
            make_voice_call(to=phone, script=voice_script)
            channels_used.append("voice")
            await log_event(
                lead_id=state["lead_id"],
                node="send_outreach",
                description=f"Voice call made to {phone}",
                channel="voice"
            )
        except Exception as e:
            print(f"[send_outreach] Voice call failed: {e}")

    # ── Update MongoDB ─────────────────────────────────────────────────
    await update_lead(state["lead_id"], {
        "status": "contacted",
        "outreach_sent": True,
        "channels_used": channels_used
    })

    print(f"[send_outreach] Done. Channels used: {channels_used}")
    return {**state, "outreach_sent": True}
