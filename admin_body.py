def admin_failure_message(failures, timestamp, summary=""):
    error_rows = "".join(
        f'<tr><td style="padding:7px 10px; color:#374151; border-bottom:1px solid #f1f5f9; font-weight:500;">{name}</td>'
        f'<td style="padding:7px 10px; color:#dc2626; border-bottom:1px solid #f1f5f9; font-family:monospace; font-size:12px; word-break:break-all;">{err}</td></tr>'
        for name, err in failures
    )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9; padding:24px 0;">
<tr><td>
<table width="620" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto;">

    <tr>
        <td style="background:#7f1d1d; border-radius:12px 12px 0 0; padding:24px 32px;">
            <div style="font-size:11px; color:#fca5a5; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">CreditOS Admin Alert</div>
            <div style="font-size:20px; font-weight:700; color:#ffffff;">API Flow Failed</div>
            <div style="font-size:13px; color:#fca5a5; margin-top:4px;">Timestamp: {timestamp}</div>
        </td>
    </tr>

    <tr>
        <td style="background:#ffffff; padding:28px 32px;">

            <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:14px 18px; margin-bottom:20px;">
                <div style="font-size:13px; font-weight:600; color:#dc2626; margin-bottom:4px;">Failure Summary</div>
                <div style="font-size:13px; color:#374151;">{summary or "See error details below."}</div>
            </div>

            <h3 style="font-size:13px; font-weight:600; color:#374151; margin:0 0 8px 0; text-transform:uppercase; letter-spacing:0.5px;">Error Details</h3>
            <table style="width:100%; border-collapse:collapse; font-size:13px; border:1px solid #e5e7eb; border-radius:8px; overflow:hidden;">
                <thead>
                    <tr style="background:#fef2f2;">
                        <th style="padding:7px 10px; text-align:left; color:#9ca3af; font-weight:600; width:120px; border-bottom:1px solid #e5e7eb;">Step</th>
                        <th style="padding:7px 10px; text-align:left; color:#9ca3af; font-weight:600; border-bottom:1px solid #e5e7eb;">Error</th>
                    </tr>
                </thead>
                <tbody>
                    {error_rows or '<tr><td colspan="2" style="padding:10px; color:#9ca3af; font-style:italic;">No additional details.</td></tr>'}
                </tbody>
            </table>

            <div style="margin-top:16px; background:#fffbeb; border-left:3px solid #f59e0b; padding:10px 14px; border-radius:0 6px 6px 0;">
                <span style="font-size:12px; color:#92400e;">
                    The error.log file is attached for full stack trace details.
                    Report data may be <strong>incomplete</strong>.
                </span>
            </div>

        </td>
    </tr>

    <tr>
        <td style="background:#f8fafc; border-top:1px solid #e5e7eb; border-radius:0 0 12px 12px; padding:16px 32px;">
            <p style="font-size:12px; color:#9ca3af; margin:0;">
                Admin-only alert — do not forward.<br>
                <strong style="color:#64748b;">CreditOS Automation</strong>
            </p>
        </td>
    </tr>

</table>
</td></tr>
</table>

</body>
</html>"""


def workflow_failure_message(failures, timestamp, summary=""):
    error_rows = "".join(
        f'<tr><td style="padding:7px 10px; color:#374151; border-bottom:1px solid #f1f5f9; font-weight:500;">{name}</td>'
        f'<td style="padding:7px 10px; color:#dc2626; border-bottom:1px solid #f1f5f9; font-family:monospace; font-size:12px; word-break:break-all;">{err}</td></tr>'
        for name, err in failures
    )

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9; padding:24px 0;">
<tr><td>
<table width="620" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto;">

    <tr>
        <td style="background:#7f1d1d; border-radius:12px 12px 0 0; padding:24px 32px;">
            <div style="font-size:11px; color:#fca5a5; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">CreditOS Admin Alert</div>
            <div style="font-size:20px; font-weight:700; color:#ffffff;">Workflow Exception</div>
            <div style="font-size:13px; color:#fca5a5; margin-top:4px;">Timestamp: {timestamp}</div>
        </td>
    </tr>

    <tr>
        <td style="background:#ffffff; padding:28px 32px;">

            <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:14px 18px; margin-bottom:20px;">
                <div style="font-size:13px; font-weight:600; color:#dc2626; margin-bottom:4px;">Root Cause</div>
                <div style="font-size:13px; color:#374151;">{summary or "Unexpected error during workflow execution."}</div>
            </div>

            <h3 style="font-size:13px; font-weight:600; color:#374151; margin:0 0 8px 0; text-transform:uppercase; letter-spacing:0.5px;">Exception Details</h3>
            <table style="width:100%; border-collapse:collapse; font-size:13px; border:1px solid #e5e7eb; border-radius:8px; overflow:hidden;">
                <thead>
                    <tr style="background:#fef2f2;">
                        <th style="padding:7px 10px; text-align:left; color:#9ca3af; font-weight:600; width:120px; border-bottom:1px solid #e5e7eb;">Step</th>
                        <th style="padding:7px 10px; text-align:left; color:#9ca3af; font-weight:600; border-bottom:1px solid #e5e7eb;">Error</th>
                    </tr>
                </thead>
                <tbody>
                    {error_rows or '<tr><td colspan="2" style="padding:10px; color:#9ca3af; font-style:italic;">No additional details.</td></tr>'}
                </tbody>
            </table>

            <div style="margin-top:16px; background:#fffbeb; border-left:3px solid #f59e0b; padding:10px 14px; border-radius:0 6px 6px 0;">
                <span style="font-size:12px; color:#92400e;">
                    The error.log file is attached. Excel report was <strong>not generated</strong>.
                </span>
            </div>

        </td>
    </tr>

    <tr>
        <td style="background:#f8fafc; border-top:1px solid #e5e7eb; border-radius:0 0 12px 12px; padding:16px 32px;">
            <p style="font-size:12px; color:#9ca3af; margin:0;">
                Admin-only alert — do not forward.<br>
                <strong style="color:#64748b;">CreditOS Automation</strong>
            </p>
        </td>
    </tr>

</table>
</td></tr>
</table>

</body>
</html>"""