import logging
import smtplib
from email.message import EmailMessage

from .config import settings

logger = logging.getLogger(__name__)


def _send_email(message: EmailMessage) -> bool:
    """
    Sendet eine E-Mail über den konfigurierten SMTP-Server.

    Wichtig:
    SMTP-Passwort / SMTP-Key wird niemals geloggt.
    """
    if not all([
        settings.SMTP_HOST,
        settings.SMTP_USER,
        settings.SMTP_PASSWORD,
        settings.SENDER_EMAIL,
    ]):
        logger.error(
            "SMTP ist nicht vollständig konfiguriert. "
            "SMTP_HOST=%s, SMTP_USER=%s, SMTP_PASSWORD=%s, SENDER_EMAIL=%s",
            bool(settings.SMTP_HOST),
            bool(settings.SMTP_USER),
            bool(settings.SMTP_PASSWORD),
            bool(settings.SENDER_EMAIL),
        )
        return False

    try:
        logger.info(
            "SMTP-Verbindung zu %s:%s wird aufgebaut...",
            settings.SMTP_HOST,
            settings.SMTP_PORT,
        )

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=15,
        ) as smtp:

            # SMTP-Verbindung initialisieren
            smtp.ehlo()

            # STARTTLS aktivieren
            smtp.starttls()

            # Nach STARTTLS erneut EHLO
            smtp.ehlo()

            logger.info("SMTP STARTTLS erfolgreich. Login wird versucht...")

            # Mit Brevo SMTP-Login + SMTP-Key anmelden
            smtp.login(
                settings.SMTP_USER,
                settings.SMTP_PASSWORD,
            )

            logger.info("SMTP-Login erfolgreich.")

            # E-Mail senden
            smtp.send_message(message)

            logger.info(
                "E-Mail erfolgreich gesendet an %s",
                message["To"],
            )

        return True

    except smtplib.SMTPAuthenticationError as exc:
        logger.error(
            "SMTP-Authentifizierung fehlgeschlagen: "
            "Code=%s, Error=%s",
            exc.smtp_code,
            exc.smtp_error.decode(errors="replace")
            if isinstance(exc.smtp_error, bytes)
            else exc.smtp_error,
        )
        return False

    except smtplib.SMTPSenderRefused as exc:
        logger.error(
            "SMTP-Absender wurde abgelehnt: "
            "Code=%s, Sender=%s, Error=%s",
            exc.smtp_code,
            exc.sender,
            exc.smtp_error.decode(errors="replace")
            if isinstance(exc.smtp_error, bytes)
            else exc.smtp_error,
        )
        return False

    except smtplib.SMTPRecipientsRefused as exc:
        logger.error(
            "SMTP-Empfänger wurde abgelehnt: %s",
            exc.recipients,
        )
        return False

    except smtplib.SMTPServerDisconnected as exc:
        logger.error(
            "SMTP-Server hat die Verbindung getrennt: %s",
            exc,
        )
        return False

    except smtplib.SMTPException as exc:
        logger.exception(
            "Allgemeiner SMTP-Fehler: %s",
            exc,
        )
        return False

    except TimeoutError as exc:
        logger.error(
            "SMTP-Verbindung Timeout: %s",
            exc,
        )
        return False

    except OSError as exc:
        logger.exception(
            "Netzwerkfehler beim SMTP-Versand: %s",
            exc,
        )
        return False

    except Exception as exc:
        logger.exception(
            "Unerwarteter Fehler beim E-Mail-Versand: %s",
            exc,
        )
        return False


def send_order_email(
    recipient: str,
    order_id: int,
    customer_name: str,
) -> bool:
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

    return _send_email(message)


def send_admin_contact_email(
    recipient: str,
    subject: str,
    body: str,
    customer_name: str,
) -> bool:
    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = settings.SENDER_EMAIL
    message["To"] = recipient

    full_body = (
        f"Hallo {customer_name},\n\n"
        f"{body}\n\n"
        "Viele Grüße\n"
        "Replione"
    )

    message.set_content(full_body)

    return _send_email(message)
