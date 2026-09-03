import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_EMAIL

def send_email(to_email: str, subject: str, body_text: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"Mock Email to {to_email}: {subject}")
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body_text, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def send_order_confirmation(to_email: str, user_name: str, order_number: str, item_count: int):
    subject = f"Replione - Bestellung {order_number}"
    body = f"""Hallo {user_name},
deine Bestellung wurde erfolgreich aufgenommen.

Bestellnummer: {order_number}
Anzahl Produkte: {item_count}
Zahlungsart: Barzahlung

Wir kümmern uns nun um die Beschaffung deiner gewünschten Produkte.

Dein Replione Team
"""
    send_email(to_email, subject, body)

def send_status_update(to_email: str, user_name: str, order_number: str, status: str):
    subject = f"Replione - Status Update: {order_number}"
    body = f"""Hallo {user_name},
der Status deiner Bestellung wurde aktualisiert.

Bestellnummer: {order_number}
Neuer Status: {status}

Dein Replione Team
"""
    send_email(to_email, subject, body)
