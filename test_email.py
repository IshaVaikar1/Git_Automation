# email_sender.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

logger = logging.getLogger("automation")

def build_subject(report_type, start_date, end_date):
    if start_date != end_date:
        report_type = "range"
    report_type = report_type.lower()

    if report_type == "daily":
        return f"BSA Daily Usage Report: {start_date}"

    if report_type == "weekly":
        return f"BSA Weekly Usage Report: {start_date} to {end_date}"

    return f"BSA Usage Report: {start_date} to {end_date}"

def send_email(host, port, user, password, recipients, subject, body, attachments=None):
    
    # ----- FROM ADDRESS -----
    # AWS SES version (requires verified email)
    # from_addr = os.getenv("SES_FROM_EMAIL", user)

    # Gmail version (sender = login email)
    from_addr = user

    try:

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

        # ----- SMTP SEND -----
        try:
            server = smtplib.SMTP(host, int(port))
            server.starttls()

            # Gmail login
            server.login(user, password)

            # SES login (same call but different credentials)
            # server.login(user, password)

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