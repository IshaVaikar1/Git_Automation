# email_sender.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

logger = logging.getLogger("automation")


# ---------------- SUBJECT BUILDER ---------------- #
def build_subject(report_type, start_date, end_date):
    if start_date != end_date:
        report_type = "range"
    report_type = report_type.lower()

    if report_type == "daily":
        return f"BSA Daily Usage Report: {start_date}"

    if report_type == "weekly":
        return f"BSA Weekly Usage Report: {start_date} to {end_date}"

    return f"BSA Usage Report: {start_date} to {end_date}"


# ---------------- DASHBOARD BUILDER ---------------- #
def build_dashboard_html(body, analysis):
    if not analysis:
        return body

    total = analysis.get("total", 0)
    success = analysis.get("success", 0)
    failed = analysis.get("failed", 0)
    success_rate = analysis.get("success_rate", 0)
    failure_reasons = analysis.get("failure_reasons", {})
    bank_stats = analysis.get("bank_stats", {})

    # Progress bar
    filled = int(success_rate // 10)
    bar = "█" * filled + "░" * (10 - filled)

    # Failure breakdown
    failure_html = "".join(
        f"<li>{k}: {v}</li>" for k, v in failure_reasons.items()
    ) or "<li>No failures</li>"

    # Bank table
    bank_rows = ""
    for bank, stats in bank_stats.items():
        bank_rows += f"""
        <tr>
            <td>{bank}</td>
            <td>{stats['total']}</td>
            <td style="color:green;">{stats['success']}</td>
            <td style="color:red;">{stats['failed']}</td>
        </tr>
        """

    # Insights
    top_failure = "None"
    if failure_reasons:
        top_failure = max(failure_reasons, key=failure_reasons.get)

    insights_html = f"""
    <h3>Key Insights</h3>
    <ul>
        <li>System success rate is {success_rate}%</li>
        <li>Total failed cases: {failed}</li>
        <li>Primary failure reason: {top_failure}</li>
    </ul>
    """

    return f"""
    <html>
    <body style="font-family: Arial; background:#f4f6f8; padding:20px;">

        <div style="background:white;padding:20px;border-radius:10px;">

            <h2>BSA Report Summary</h2>

            <div style="display:flex; gap:20px; margin-bottom:15px;">
                <div style="background:#e8f5e9;padding:10px;border-radius:8px;">
                    <b>Total</b><br>{total}
                </div>
                <div style="background:#e3f2fd;padding:10px;border-radius:8px;">
                    <b>Success</b><br>{success}
                </div>
                <div style="background:#ffebee;padding:10px;border-radius:8px;">
                    <b>Failed</b><br>{failed}
                </div>
            </div>

            <p><b>Success Rate:</b> {bar} {success_rate}%</p>

            {insights_html}

            <h3>Failure Breakdown</h3>
            <ul>
                {failure_html}
            </ul>

            <h3>Bank-wise Analysis</h3>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                <tr style="background:#f2f2f2;">
                    <th>Bank</th>
                    <th>Total</th>
                    <th>Success</th>
                    <th>Failed</th>
                </tr>
                {bank_rows}
            </table>

            <hr style="margin:20px 0;">

            {body}

        </div>

    </body>
    </html>
    """


# ---------------- EMAIL SENDER ---------------- #
def send_email(host, port, user, password, recipients, subject, body, analysis=None, attachments=None):

    # Gmail default sender
    from_addr = user

    # Optional: SES override
    if os.getenv("SES_FROM_EMAIL"):
        from_addr = os.getenv("SES_FROM_EMAIL")

    try:
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        final_html = body

        msg.attach(MIMEText(final_html, "html"))

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

        # ----- SMTP SEND -----
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