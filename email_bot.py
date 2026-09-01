import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def send_order_confirmation(to_email: str, user_name: str, order_number: str, items: list):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[Email-Bot]: Keine Zugangsdaten gesetzt. E-Mail wird übersprungen.")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Bestellbestätigung — {order_number}"
        msg["From"] = f"Replione <{SMTP_USER}>"
        msg["To"] = to_email

        item_rows = ""
        for i, item in enumerate(items, 1):
            size = item.get("size", "—")
            color = item.get("color", "—")
            link = item.get("link", "Kein Link")
            notes = item.get("notes", "Keine Notizen")
            has_img = "Ja" if item.get("image") else "Nein"
            
            item_rows += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px;">#{i}</td>
                <td style="padding: 10px;"><b>Größe:</b> {size}<br><b>Farbe:</b> {color}</td>
                <td style="padding: 10px;"><a href="{link}" target="_blank">{link[:35]}...</a><br><small><b>Screenshot vorhanden:</b> {has_img}</small></td>
                <td style="padding: 10px;">{notes}</td>
            </tr>
            """

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 650px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 15px;">
            <h2 style="color: #171717;">Vielen Dank für deine Bestellung, {user_name}!</h2>
            <p style="color: #555;">Deine Bestellung <b>{order_number}</b> ist erfolgreich bei uns eingegangen und wird nun bearbeitet.</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <h3>Bestellte Artikel</h3>
            <table style="width: 100%; text-align: left; border-collapse: collapse; font-size: 14px;">
                <thead>
                    <tr style="background: #f6f6f4;">
                        <th style="padding: 8px;">Pos</th>
                        <th style="padding: 8px;">Details</th>
                        <th style="padding: 8px;">Link / Bild</th>
                        <th style="padding: 8px;">Hinweise</th>
                    </tr>
                </thead>
                <tbody>
                    {item_rows}
                </tbody>
            </table>
            <br>
            <p style="color: #777; font-size: 13px;">Bei Fragen antworte einfach auf diese E-Mail.</p>
            <p>Beste Grüße,<br><b>Dein Replione Team</b></p>
        </div>
        """

        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
            print(f"[Email-Bot]: Bestätigung erfolgreich an {to_email} gesendet.")
    except Exception as e:
        print(f"[Email-Bot Fehler]: {e}")