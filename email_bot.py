import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp-mail.outlook.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587").strip())
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()

def send_order_confirmation(to_email: str, user_name: str, order_number: str, items: list):
    print(f"-> [Email-Bot]: Starte Versand für {order_number} an {to_email}...", flush=True)

    if not SMTP_USER or not SMTP_PASSWORD:
        print("[Email-Bot Info]: SMTP_USER oder SMTP_PASSWORD nicht konfiguriert. E-Mail wird übersprungen.", flush=True)
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
            notes = item.get("notes", "Keine Angaben")
            has_img = "Ja (hochgeladen)" if item.get("image") else "Nein"

            item_rows += f"""
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 10px; font-weight: bold; color: #111827;">#{i}</td>
                <td style="padding: 10px; color: #374151;"><b>Größe:</b> {size}<br><b>Farbe:</b> {color}</td>
                <td style="padding: 10px; color: #374151;"><a href="{link}" target="_blank" style="color: #2563eb;">Link öffnen</a><br><small style="color: #6b7280;">Screenshot: {has_img}</small></td>
                <td style="padding: 10px; color: #4b5563;">{notes}</td>
            </tr>
            """

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 620px; margin: 0 auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden;">
            <div style="background: #111827; padding: 24px; text-align: center; color: #ffffff;">
                <h1 style="margin: 0; font-size: 24px; letter-spacing: 1px;">REPLIONE</h1>
                <p style="margin: 6px 0 0 0; color: #9ca3af; font-size: 14px;">Bestellbestätigung</p>
            </div>
            <div style="padding: 24px;">
                <h2 style="font-size: 18px; color: #111827; margin-top: 0;">Vielen Dank für deine Bestellung, {user_name}!</h2>
                <p style="color: #4b5563; font-size: 14px; line-height: 1.5;">
                    Deine Bestellung mit der Nummer <b>{order_number}</b> ist erfolgreich bei uns eingegangen und wird derzeit geprüft. Den aktuellen Fortschritt kannst du jederzeit in deinem Kundenkonto verfolgen.
                </p>
                <div style="margin: 24px 0;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px; text-align: left;">
                        <thead>
                            <tr style="background: #f9fafb; border-bottom: 2px solid #e5e7eb; color: #4b5563;">
                                <th style="padding: 10px;">Pos</th>
                                <th style="padding: 10px;">Details</th>
                                <th style="padding: 10px;">Link</th>
                                <th style="padding: 10px;">Hinweise</th>
                            </tr>
                        </thead>
                        <tbody>{item_rows}</tbody>
                    </table>
                </div>
                <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 24px 0;">
                <p style="color: #6b7280; font-size: 12px; margin: 0;">
                    Fragen oder Änderungswünsche? Antworte einfach direkt auf diese E-Mail.<br>
                    Dein <b>Replione Team</b>
                </p>
            </div>
        </div>
        """
        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=12)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        print(f"✓ [Email-Bot ERFOLG]: Bestätigung erfolgreich an {to_email} versendet.", flush=True)

    except Exception as e:
        print(f"❌ [Email-Bot FEHLER]: {type(e).__name__} -> {e}", flush=True)
