import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Fest kodierte Brevo-Settings für fehlerfreien Versand
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp-relay.brevo.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587").strip())
SMTP_USER = os.getenv("SMTP_USER", "b7760d001@smtp-brevo.com").strip()
# WICHTIG: Die Absenderadresse muss bei Brevo verifiziert sein!
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "dlugoschmario@icloud.com").strip()

SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()

def send_order_confirmation(to_email: str, user_name: str, order_number: str, items: list):
    print(f"-> [Email-Bot]: Starte Versand für {order_number} an {to_email}...", flush=True)

    if not SMTP_PASSWORD:
        print("[Email-Bot Info]: SMTP_PASSWORD nicht konfiguriert. E-Mail wird übersprungen.", flush=True)
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Bestellbestätigung — {order_number}"
        msg["From"] = f"Replione <{SENDER_EMAIL}>"
        msg["To"] = to_email

        item_rows = ""
        for i, item in enumerate(items, 1):
            size = item.get("size", "—")
            color = item.get("color", "—")
            link = item.get("link", "Kein Link")
            notes = item.get("notes", "Keine Angaben")
            
            link_html = f'<a href="{link}" target="_blank" style="color: #e5b900; font-weight:bold;">Link öffnen</a>' if link else "Kein Link"

            item_rows += f"""
            <tr style="border-bottom: 1px solid #e5e7eb;">
                <td style="padding: 12px; font-weight: bold; color: #171717;">#{i}</td>
                <td style="padding: 12px; color: #555;"><b>Größe:</b> {size}<br><b>Farbe:</b> {color}</td>
                <td style="padding: 12px; color: #555;">{link_html}</td>
                <td style="padding: 12px; color: #888; font-size: 12px;">{notes}</td>
            </tr>
            """

        html_content = f"""
        <div style="font-family: 'Inter', Arial, sans-serif; max-width: 620px; margin: 0 auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 20px; overflow: hidden; box-shadow: 0 14px 40px rgba(0,0,0,.05);">
            <div style="background: #171717; padding: 25px; text-align: center; color: #ffffff;">
                <h1 style="margin: 0; font-size: 24px; letter-spacing: -1px;">repl<span style="color: #e5b900;">i</span>one</h1>
                <p style="margin: 5px 0 0 0; color: #888; font-size: 14px;">Bestellbestätigung</p>
            </div>
            <div style="padding: 30px;">
                <h2 style="font-size: 20px; color: #171717; margin-top: 0; letter-spacing: -0.5px;">Vielen Dank, {user_name}!</h2>
                <p style="color: #555; font-size: 15px; line-height: 1.6;">
                    Deine Bestellung <b>{order_number}</b> ist erfolgreich eingegangen. Wir prüfen die Angaben und kümmern uns um den nächsten Schritt.
                </p>
                <div style="margin: 25px 0; background: #f6f6f4; border-radius: 15px; padding: 15px;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 2px solid #dedede; color: #171717;">
                                <th style="padding: 10px;">Pos</th>
                                <th style="padding: 10px;">Details</th>
                                <th style="padding: 10px;">Link</th>
                                <th style="padding: 10px;">Notizen</th>
                            </tr>
                        </thead>
                        <tbody>{item_rows}</tbody>
                    </table>
                </div>
                <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 25px 0;">
                <p style="color: #888; font-size: 13px; margin: 0; text-align: center;">
                    Fragen zur Bestellung? Antworte einfach auf diese E-Mail.<br>
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
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"✓ [Email-Bot ERFOLG]: Bestätigung erfolgreich an {to_email} versendet.", flush=True)

    except Exception as e:
        print(f"❌ [Email-Bot FEHLER]: {type(e).__name__} -> {e}", flush=True)
