import smtplib
from email.message import EmailMessage
from .config import settings
def send_order_email(
    recipient: str,
    order_id: int,
    customer_name: str,
) -> bool:
    if not all(
        [
            settings.SMTP_HOST,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
            settings.SENDER_EMAIL,
        ]
    ):
        return False
    message = EmailMessage()
    message["Subject"] = (
        f"Replione – Bestellung #{order_id} eingegangen"
    )
    message["From"] = settings.SENDER_EMAIL
    message["To"] = recipient
    message.set_content(
        f"""Hallo {customer_name},
deine Bestellung bei Replione ist eingegangen.
Bestellnummer: #{order_id}
Zahlungsart: Barzahlung
Status: Eingegangen
Wir kümmern uns um die weitere Bearbeitung.
Viele Grüße
Replione
"""
    )
    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=15,
        ) as smtp:
            smtp.starttls()
            smtp.login(
                settings.SMTP_USER,
                settings.SMTP_PASSWORD,
            )
            smtp.send_message(message)
        return True
    except Exception:
        return False

def send_admin_contact_email(
    recipient: str,
    subject: str,
    body: str,
    customer_name: str,
) -> bool:
    if not all(
        [
            settings.SMTP_HOST,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
            settings.SENDER_EMAIL,
        ]
    ):
        return False
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.SENDER_EMAIL
    message["To"] = recipient

    full_body = f"Hallo {customer_name},\n\n{body}\n\nViele Grüße\nReplione"
    message.set_content(full_body)

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=15,
        ) as smtp:
            smtp.starttls()
            smtp.login(
                settings.SMTP_USER,
                settings.SMTP_PASSWORD,
            )
            smtp.send_message(message)
        return True
    except Exception:
        import logging
        logging.exception("Failed to send admin contact email")
        return False
