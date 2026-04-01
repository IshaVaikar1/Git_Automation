def failure_message(report_date):
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9; padding:24px 0;">
<tr><td>
<table width="580" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto;">

    <tr>
        <td style="background:#0f172a; border-radius:12px 12px 0 0; padding:24px 32px;">
            <div style="font-size:11px; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">CreditOS Automation</div>
            <div style="font-size:20px; font-weight:700; color:#ffffff;">BSA Report — Generation Failed</div>
            <div style="font-size:13px; color:#94a3b8; margin-top:4px;">Date: {report_date}</div>
        </td>
    </tr>

    <tr>
        <td style="background:#ffffff; padding:28px 32px;">

            <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:16px 20px; margin-bottom:20px;">
                <div style="font-size:14px; font-weight:600; color:#dc2626; margin-bottom:6px;">⚠ Report Could Not Be Generated</div>
                <div style="font-size:13px; color:#374151; line-height:1.6;">
                    The BSA Usage Report for <strong>{report_date}</strong> could not be generated due to a system issue.
                    We are investigating and will resolve this as soon as possible.
                </div>
            </div>

            <p style="font-size:13px; color:#6b7280; margin:0;">
                You will be notified once the issue is resolved. Thank you for your patience.
            </p>

        </td>
    </tr>

    <tr>
        <td style="background:#f8fafc; border-top:1px solid #e5e7eb; border-radius:0 0 12px 12px; padding:16px 32px;">
            <p style="font-size:12px; color:#9ca3af; margin:0;">
                This is an automated notification from CreditOS.<br>
                <strong style="color:#64748b;">CreditOS Team</strong>
            </p>
        </td>
    </tr>

</table>
</td></tr>
</table>

</body>
</html>"""