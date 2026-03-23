# email_sender.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

logger = logging.getLogger("automation")

def send_email(host, port, user, password, recipients, subject, body, attachments=None):
    from_addr = os.getenv("SMTP_HOST", user)
    try:
        # ----- FROM ADDRESS (SES requires verified identity) -----
        from_addr = os.getenv("SES_FROM_EMAIL", user)

        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        # ----- Attach files -----
        for path in attachments or []:
            if os.path.exists(path):
                part = MIMEBase("application", "octet-stream")
                part.set_payload(open(path, "rb").read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(path)}"
                )
                msg.attach(part)
                logger.info(f"Attached file: {path}")
            else:
                logger.warning(f"[ATTACHMENT MISSING] {path} does not exist")

        # ----- SES SMTP SEND -----
        try:
            server = smtplib.SMTP(host, int(port))
            server.starttls()
            server.login(user, password)   # SES SMTP credentials
            server.sendmail(from_addr, recipients, msg.as_string())
            server.quit()
            logger.info(f"Email sent to {recipients}")

        except Exception:
            logger.error(
                f"[EMAIL SEND ERROR] Failed sending email to {recipients}",
                exc_info=True
            )
            raise

    except Exception:
        logger.error(
            f"[EMAIL ERROR] Unexpected failure while preparing email to {recipients}",
            exc_info=True
        )
        raise
