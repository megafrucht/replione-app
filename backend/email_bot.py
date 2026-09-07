import logging
import smtplib
from email.message import EmailMessage

from .config import settings

logger = logging.getLogger(__name__)


def send_test_email(recipient: str) -> bool:
    """
    Einfacher SMTP-Test.
    Sendet eine Test-Mail an den angegebenen Empfänger.
    """

    # Prüfen, ob alle SMTP-Werte vorhanden sind
    missing = []

    if not settings.SMTP_HOST:
        missing.append("SMTP_HOST")

    if not settings.SMTP_USER:
        missing.append("SMTP_USER")

    if not settings.SMTP_PASSWORD:
        missing.append("SMTP_PASSWORD")

    if not settings.SENDER_EMAIL:
        missing.append("SENDER_EMAIL")

    if missing:
        logger.error(
            "SMTP-Konfiguration unvollständig. Fehlend: %s",
            ", ".join(missing),
        )
        return False

    message = EmailMessage()

    message["Subject"] = "Replione – SMTP Test"
    message["From"] = settings.SENDER_EMAIL
    message["To"] = recipient

    message.set_content(
        """Hallo,

dies ist eine Test-E-Mail von Replione.

Wenn du diese E-Mail erhalten hast, funktioniert die SMTP-Verbindung.

Viele Grüße
Replione
"""
    )

    try:
        logger.info(
            "Verbinde mit SMTP-Server %s:%s",
            settings.SMTP_HOST,
            settings.SMTP_PORT,
        )

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=15,
        ) as smtp:

            # SMTP initialisieren
            smtp.ehlo()

            # STARTTLS
            smtp.starttls()

            # Nach STARTTLS erneut identifizieren
            smtp.ehlo()

            logger.info("STARTTLS erfolgreich.")

            # SMTP-Login
            smtp.login(
                settings.SMTP_USER,
                settings.SMTP_PASSWORD,
            )

            logger.info("SMTP-Login erfolgreich.")

            # Mail senden
            smtp.send_message(message)

            logger.info(
                "Test-E-Mail erfolgreich an %s gesendet.",
                recipient,
            )

        return True

    except smtplib.SMTPAuthenticationError as exc:
        error = (
            exc.smtp_error.decode(errors="replace")
            if isinstance(exc.smtp_error, bytes)
            else str(exc.smtp_error)
        )

        logger.error(
            "SMTP-Authentifizierung fehlgeschlagen: "
            "Code=%s, Fehler=%s",
            exc.smtp_code,
            error,
        )
        return False

    except smtplib.SMTPSenderRefused as exc:
        error = (
            exc.smtp_error.decode(errors="replace")
            if isinstance(exc.smtp_error, bytes)
            else str(exc.smtp_error)
        )

        logger.error(
            "SMTP-Absender abgelehnt: "
            "Code=%s, Fehler=%s",
            exc.smtp_code,
            error,
        )
        return False

    except smtplib.SMTPRecipientsRefused as exc:
        logger.error(
            "SMTP-Empfänger abgelehnt: %s",
            exc.recipients,
        )
        return False

    except smtplib.SMTPServerDisconnected as exc:
        logger.error(
            "SMTP-Server hat Verbindung getrennt: %s",
            exc,
        )
        return False

    except smtplib.SMTPException as exc:
        logger.exception(
            "SMTP-Fehler: %s",
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
            "Unerwarteter Fehler beim SMTP-Versand: %s",
            exc,
        )
        return False
