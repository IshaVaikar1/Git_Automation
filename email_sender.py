# email_sender.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

logger = logging.getLogger("automation")


# ---------------- EMAIL SENDER ---------------- #
def send_email(host, port, user, password, recipients, subject, body, analysis=None, attachments=None):

    try:
        from_addr = os.getenv("SES_FROM_EMAIL", user)

        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        # ----- Attach files -----
        for path in attachments or []:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())

                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(path)}"
                )
                msg.attach(part)
                logger.info(f"Attached file: {path}")
            else:
                logger.warning(f"[ATTACHMENT MISSING] {path} does not exist")

        # ----- SEND EMAIL -----
        server = smtplib.SMTP(host, int(port))
        server.starttls()
        server.login(user, password)
        server.sendmail(from_addr, recipients, msg.as_string())
        server.quit()

        logger.info(f"Email sent to {recipients}")

    except Exception:
        logger.error(
            f"[EMAIL ERROR] Failed sending email to {recipients}",
            exc_info=True
        )
        raise