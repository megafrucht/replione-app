import logging
import httpx
from .config import settings

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_order_email(
    recipient: str,
    order_id: int,
    customer_name: str,
) -> bool:
    api_key = settings.BREVO_API_KEY
    sender_email = settings.SENDER_EMAIL
    if not api_key or not sender_email:
        return False

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    payload = {
        "sender": {
            "name": settings.APP_NAME,
            "email": sender_email,
        },
        "to": [
            {
                "email": recipient,
                "name": customer_name,
            }
        ],
        "subject": f"Replione – Bestellung #{order_id} eingegangen",
        "textContent": f"""Hallo {customer_name},

deine Bestellung bei Replione ist eingegangen.

Bestellnummer: #{order_id}
Zahlungsart: Barzahlung
Status: Eingegangen

Wir kümmern uns um die weitere Bearbeitung.

Viele Grüße
Replione
""",
    }

    try:
        response = httpx.post(
            BREVO_API_URL,
            headers=headers,
            json=payload,
            timeout=15.0,
        )
        if response.status_code in (200, 201, 202):
            return True
        logging.error(
            "Brevo API error: status %s, response %s",
            response.status_code,
            response.text,
        )
        return False
    except Exception:
        logging.exception("Failed to send order email via Brevo API")
        return False


def send_admin_contact_email(
    recipient: str,
    subject: str,
    body: str,
    customer_name: str,
) -> bool:
    api_key = settings.BREVO_API_KEY
    sender_email = settings.SENDER_EMAIL
    if not api_key or not sender_email:
        return False

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    full_body = f"Hallo {customer_name},\n\n{body}\n\nViele Grüße\nReplione"
    payload = {
        "sender": {
            "name": settings.APP_NAME,
            "email": sender_email,
        },
        "to": [
            {
                "email": recipient,
                "name": customer_name,
            }
        ],
        "subject": subject,
        "textContent": full_body,
    }

    try:
        response = httpx.post(
            BREVO_API_URL,
            headers=headers,
            json=payload,
            timeout=15.0,
        )
        if response.status_code in (200, 201, 202):
            return True
        logging.error(
            "Brevo API error: status %s, response %s",
            response.status_code,
            response.text,
        )
        return False
    except Exception:
        logging.exception("Failed to send admin contact email via Brevo API")
        return False
