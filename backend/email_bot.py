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
