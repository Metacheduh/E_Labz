"""
E-Labz Email Engine — SMTP/IMAP via Gmail App Password
Send emails, read inbox, nurture leads. No browser needed.

Usage:
    from orchestrator.utils.email_client import send_email, read_inbox
    send_email("user@example.com", "Subject", "Body text")
    emails = read_inbox(count=10)
"""

import os
import smtplib
import imaplib
import email as email_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load env
_ENV = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(_ENV, override=True)

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
IMAP_SERVER = "imap.gmail.com"


def send_email(
    to: str,
    subject: str,
    body: str,
    html: bool = False,
    reply_to: str = "",
) -> dict:
    """Send an email via Gmail SMTP. Returns status dict."""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        return {"status": "failed", "reason": "Gmail credentials not configured"}

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"E-Labz <{GMAIL_ADDRESS}>"
        msg["To"] = to
        msg["Subject"] = subject
        if reply_to:
            msg["Reply-To"] = reply_to

        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body, content_type))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        print(f"  [EMAIL] Sent to {to}: {subject}")
        return {"status": "sent", "to": to, "subject": subject}

    except smtplib.SMTPAuthenticationError:
        return {"status": "failed", "reason": "Gmail auth failed — check app password"}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}


def read_inbox(count: int = 10, folder: str = "INBOX") -> list[dict]:
    """Read recent emails from Gmail via IMAP. Returns list of dicts."""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        return []

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=10)
        mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        mail.select(folder, readonly=True)

        _, data = mail.search(None, "ALL")
        ids = data[0].split()

        # Get the last N emails
        results = []
        for eid in ids[-count:]:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            raw = msg_data[0][1]
            msg = email_lib.message_from_bytes(raw)

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="replace")

            results.append({
                "from": msg["From"],
                "to": msg["To"],
                "subject": msg["Subject"],
                "date": msg["Date"],
                "body": body[:500],  # Truncate for safety
            })

        mail.logout()
        return results

    except Exception as e:
        print(f"  [EMAIL] Read failed: {e}")
        return []


def send_lead_welcome(to: str, name: str = "there") -> dict:
    """Send welcome email to a new lead with product showcase."""
    subject = "Your free AI toolkit is here 🚀"
    body = f"""Hey {name},

Thanks for grabbing the free guide — here's what's inside:

• 9 AI agent pipelines (LeadGen, ContentEngine, SiteAudit + more)
• The exact automation stack running @AutoStackHQ 24/7
• Step-by-step deployment guide (Cloud Run + ADK)

If you want the full source code, check out the store:
→ https://autostackhq.lemonsqueezy.com

Questions? Just reply to this email.

— E-Labz Team
"""
    return send_email(to, subject, body)


def send_sale_notification(product: str, amount: float, customer: str = "") -> dict:
    """Send internal notification when a sale happens."""
    subject = f"💰 New sale: {product} (${amount:.2f})"
    body = f"""New sale just came in!

Product: {product}
Amount: ${amount:.2f}
Customer: {customer or 'Unknown'}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Check your Lemon Squeezy dashboard for details.
"""
    return send_email(GMAIL_ADDRESS, subject, body)


if __name__ == "__main__":
    # Quick test
    result = send_email(
        GMAIL_ADDRESS,
        "🧪 E-Labz Email Test",
        "If you're reading this, the email engine works!",
    )
    print(f"Test result: {result}")
