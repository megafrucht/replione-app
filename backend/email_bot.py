import smtplib
from email.message import EmailMessage
from .config import settings

def send_test_email(recipient: str) -> bool:
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.SENDER_EMAIL]):
        return False

    message = EmailMessage()
    message["Subject"] = "Test"
    message["From"] = settings.SENDER_EMAIL
    message["To"] = recipient
    message.set_content("test")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(message)
        return True
    except Exception:
        import logging
        logging.exception("Failed to send test email")
        return False
