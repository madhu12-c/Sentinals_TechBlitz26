from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
REP_NUMBER    = os.getenv("REP_WHATSAPP_NUMBER")


def send_whatsapp(to: str, message: str) -> str:
    """Send a WhatsApp message. Returns message SID."""
    msg = twilio_client.messages.create(
        from_=WHATSAPP_FROM,
        to=to,
        body=message
    )
    return msg.sid


def notify_rep(lead_id: str, name: str, score: int, reason: str, source: str) -> str:
    """Send approval request to the sales rep."""
    score_emoji = "🔥" if score >= 8 else "👍" if score >= 5 else "❄️"

    message = (
        f"{score_emoji} *New Lead — Action Required*\n\n"
        f"*Name:* {name}\n"
        f"*Source:* {source}\n"
        f"*Score:* {score}/10\n\n"
        f"*Why:* {reason}\n\n"
        f"Reply *APPROVE* or *REJECT*\n"
        f"(Lead ID: {lead_id})"
    )

    return send_whatsapp(REP_NUMBER, message)


def send_lead_whatsapp(to: str, message: str) -> str:
    """Send WhatsApp outreach message to a lead."""
    # Ensure proper whatsapp: prefix
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"
    return send_whatsapp(to, message)


def make_voice_call(to: str, script: str) -> str:
    """Make an automated voice call to a lead using TwiML."""
    if not to.startswith("whatsapp:"):
        phone = to
    else:
        phone = to.replace("whatsapp:", "")

    twiml = f'<Response><Say voice="Polly.Aditi">{script}</Say></Response>'
    call = twilio_client.calls.create(
        twiml=twiml,
        to=phone,
        from_=WHATSAPP_FROM.replace("whatsapp:", "")
    )
    return call.sid
