from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()

sg_client = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
FROM_EMAIL = os.getenv("FROM_EMAIL", "sales@yourdomain.com")


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send a plain text email via SendGrid. Returns True on success."""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )
    try:
        response = sg_client.send(message)
        return response.status_code in (200, 202)
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False


def send_outreach_email(name: str, to_email: str, suggested_message: str) -> bool:
    """Send the AI-drafted outreach email to a lead."""
    subject = f"Hi {name} — quick note from us"
    return send_email(to_email, subject, suggested_message)


def send_followup_email(name: str, to_email: str, follow_up_count: int) -> bool:
    """Send a follow-up email when no reply received."""
    messages = [
        f"Hi {name},\n\nJust following up on my previous message. Would love to connect and see how we can help. Let me know if you have any questions!\n\nBest regards",
        f"Hi {name},\n\nI wanted to reach out one more time. If now is not the right time, no worries at all — just let me know and I won't bother you again.\n\nBest regards",
        f"Hi {name},\n\nThis will be my last follow-up. If you ever need us in the future, we're here. Wishing you all the best!\n\nBest regards"
    ]
    idx = min(follow_up_count - 1, len(messages) - 1)
    subject = f"Following up — {name}"
    return send_email(to_email, subject, messages[idx])
