def success_message(report_type, start_date, end_date, analysis=None):

    report_type = report_type.lower()

    if report_type == "daily":
        title = "BSA Daily Usage Report"
        date_text = f"{start_date}"
        period_label = start_date
    elif report_type == "weekly":
        title = "BSA Weekly Usage Report"
        date_text = f"{start_date} to {end_date}"
        period_label = f"{start_date} – {end_date}"
    else:
        title = "BSA Usage Report"
        date_text = f"{start_date} to {end_date}"
        period_label = f"{start_date} – {end_date}"

    # ---- DASHBOARD ----
    dashboard_html = ""

    if analysis:
        sh = analysis.get("system_health", {})
        failures = analysis.get("failure_intelligence", {})
        banks = analysis.get("bank_distribution", {})
        fta = analysis.get("file_type_analysis", {})
        failed_records = analysis.get("failed_records", [])
        day_wise = analysis.get("day_wise_breakdown", {})
        action_items = analysis.get("action_items", [])

        total = sh.get("total", 0)
        completed = sh.get("Completed", 0)
        failed = sh.get("failed", 0)
        submitted = sh.get("submitted", 0)
        success_rate = sh.get("success_rate", 0)
        failure_rate = sh.get("failure_rate", 0)

        # ---- Status badge ----
        if failure_rate == 0:
            status_color = "#22c55e"
            status_label = "All Systems Healthy"
            status_icon = "✓"
        elif failure_rate < 10:
            status_color = "#f59e0b"
            status_label = "Minor Issues"
            status_icon = "⚠"
        else:
            status_color = "#ef4444"
            status_label = "Attention Required"
            status_icon = "✗"

        # ---- Summary cards (table-based for email compatibility) ----
        cards_html = f"""
        <table cellpadding="0" cellspacing="0" style="width:100%; border-collapse:separate; border-spacing:8px 0;">
        <tr>
            <td style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; text-align:center; width:25%;">
                <div style="font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Total</div>
                <div style="font-size:24px; font-weight:700; color:#1e293b;">{total}</div>
            </td>
            <td style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:14px 16px; text-align:center; width:25%;">
                <div style="font-size:11px; color:#16a34a; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Completed</div>
                <div style="font-size:24px; font-weight:700; color:#15803d;">{completed}</div>
            </td>
            <td style="background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:14px 16px; text-align:center; width:25%;">
                <div style="font-size:11px; color:#dc2626; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Failed</div>
                <div style="font-size:24px; font-weight:700; color:#b91c1c;">{failed}</div>
            </td>
            <td style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:14px 16px; text-align:center; width:25%;">
                <div style="font-size:11px; color:#d97706; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Submitted</div>
                <div style="font-size:24px; font-weight:700; color:#b45309;">{submitted}</div>
            </td>
        </tr>
        </table>
        """

        # ---- Success rate bar ----
        rate_color = '#22c55e' if success_rate >= 90 else '#f59e0b' if success_rate >= 70 else '#ef4444'
        rate_bar_html = f"""
        <div style="margin-top:16px;">
            <table cellpadding="0" cellspacing="0" style="width:100%;">
                <tr>
                    <td style="font-size:12px; color:#64748b;">Success Rate</td>
                    <td style="font-size:12px; font-weight:600; color:#1e293b; text-align:right;">{success_rate}%</td>
                </tr>
            </table>
            <div style="background:#e2e8f0; border-radius:999px; height:8px; overflow:hidden; margin-top:4px;">
                <div style="width:{success_rate}%; background:{rate_color}; height:8px; border-radius:999px;"></div>
            </div>
        </div>
        """

        # ---- File type split ----
        bank_req = fta.get("bank_requests", 0)
        summ_req = fta.get("summarized_bsa_requests", 0)
        file_type_html = ""
        if bank_req or summ_req:
            file_type_html = f"""
            <table cellpadding="0" cellspacing="0" style="width:100%; margin-top:16px; border-collapse:separate; border-spacing:8px 0;">
            <tr>
                <td style="background:#f1f5f9; border-radius:6px; padding:10px 12px; width:50%;">
                    <span style="font-size:11px; color:#64748b; display:block; margin-bottom:2px;">Bank Requests</span>
                    <span style="font-size:18px; font-weight:700; color:#334155;">{bank_req}</span>
                </td>
                <td style="background:#f1f5f9; border-radius:6px; padding:10px 12px; width:50%;">
                    <span style="font-size:11px; color:#64748b; display:block; margin-bottom:2px;">BSA Summarization</span>
                    <span style="font-size:18px; font-weight:700; color:#334155;">{summ_req}</span>
                </td>
            </tr>
            </table>
            """

        # ---- Failure intelligence ----
        failure_section = ""
        if failures and failed > 0:
            top_failures = list(failures.items())[:5]
            failure_rows = ""
            for reason, count in top_failures:
                pct = round((count / failed) * 100, 1) if failed else 0
                failure_rows += f"""
                <tr>
                    <td style="padding:8px 12px; font-size:13px; color:#374151; border-bottom:1px solid #f1f5f9; max-width:260px; word-break:break-word;">{reason}</td>
                    <td style="padding:8px 12px; font-size:13px; font-weight:600; color:#b91c1c; border-bottom:1px solid #f1f5f9; text-align:center;">{count}</td>
                    <td style="padding:8px 12px; font-size:12px; color:#9ca3af; border-bottom:1px solid #f1f5f9; text-align:right;">{pct}%</td>
                </tr>
                """

            failure_section = f"""
            <div style="margin-top:24px;">
                <h3 style="font-size:13px; font-weight:600; color:#374151; margin:0 0 10px 0; text-transform:uppercase; letter-spacing:0.5px;">
                    Failure Breakdown
                </h3>
                <table style="width:100%; border-collapse:collapse; background:#fff; border:1px solid #e5e7eb; border-radius:8px; overflow:hidden;">
                    <thead>
                        <tr style="background:#fef2f2;">
                            <th style="padding:8px 12px; font-size:11px; color:#9ca3af; text-align:left; font-weight:600;">Reason</th>
                            <th style="padding:8px 12px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">Count</th>
                            <th style="padding:8px 12px; font-size:11px; color:#9ca3af; text-align:right; font-weight:600;">Share</th>
                        </tr>
                    </thead>
                    <tbody>
                        {failure_rows}
                    </tbody>
                </table>
            </div>
            """

        # ---- Bank distribution ----
        bank_section = ""
        if banks:
            valid_banks = {k: v for k, v in banks.items() if v.get("total", 0) > 0}
            if valid_banks:
                bank_rows = ""
                for bank, stats in sorted(valid_banks.items(), key=lambda x: -x[1]["total"]):
                    b_total = stats.get("total", 0)
                    b_ok = stats.get("success", 0)
                    b_fail = stats.get("failed", 0)
                    b_rate = round((b_ok / b_total) * 100, 1) if b_total else 0
                    rate_color = "#22c55e" if b_rate >= 90 else "#f59e0b" if b_rate >= 70 else "#ef4444"
                    bank_rows += f"""
                    <tr>
                        <td style="padding:8px 12px; font-size:13px; color:#374151; border-bottom:1px solid #f9fafb;">{bank}</td>
                        <td style="padding:8px 12px; font-size:13px; color:#374151; border-bottom:1px solid #f9fafb; text-align:center;">{b_total}</td>
                        <td style="padding:8px 12px; font-size:13px; color:#15803d; border-bottom:1px solid #f9fafb; text-align:center;">{b_ok}</td>
                        <td style="padding:8px 12px; font-size:13px; color:#b91c1c; border-bottom:1px solid #f9fafb; text-align:center;">{b_fail}</td>
                        <td style="padding:8px 12px; border-bottom:1px solid #f9fafb; text-align:center;">
                            <span style="font-size:12px; font-weight:600; color:{rate_color};">{b_rate}%</span>
                        </td>
                    </tr>
                    """

                bank_section = f"""
                <div style="margin-top:24px;">
                    <h3 style="font-size:13px; font-weight:600; color:#374151; margin:0 0 10px 0; text-transform:uppercase; letter-spacing:0.5px;">
                        Bank-wise Distribution
                    </h3>
                    <table style="width:100%; border-collapse:collapse; background:#fff; border:1px solid #e5e7eb; border-radius:8px; overflow:hidden;">
                        <thead>
                            <tr style="background:#f8fafc;">
                                <th style="padding:8px 12px; font-size:11px; color:#9ca3af; text-align:left; font-weight:600;">Bank</th>
                                <th style="padding:8px 12px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">Total</th>
                                <th style="padding:8px 12px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">✓ OK</th>
                                <th style="padding:8px 12px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">✗ Failed</th>
                                <th style="padding:8px 12px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            {bank_rows}
                        </tbody>
                    </table>
                </div>
                """

        # ---- Failed records section removed (moved to Digital Dashboard) ----
        failed_records_section = ""

        # ---- Day-wise breakdown (weekly reports only) ----
        day_wise_section = ""
        if report_type == "weekly" and day_wise:
            dw_rows = ""
            for day, stats in sorted(day_wise.items()):
                d_total = stats.get("total", 0)
                d_completed = stats.get("completed", 0)
                d_failed = stats.get("failed", 0)
                d_submitted = stats.get("submitted", 0)
                d_rate = round((d_completed / d_total) * 100, 1) if d_total else 0
                d_rate_color = "#22c55e" if d_rate >= 90 else "#f59e0b" if d_rate >= 70 else "#ef4444"
                dw_rows += f"""
                <tr>
                    <td style="padding:7px 10px; font-size:12px; color:#374151; border-bottom:1px solid #f1f5f9; font-weight:500;">{day}</td>
                    <td style="padding:7px 10px; font-size:12px; color:#374151; border-bottom:1px solid #f1f5f9; text-align:center;">{d_total}</td>
                    <td style="padding:7px 10px; font-size:12px; color:#15803d; border-bottom:1px solid #f1f5f9; text-align:center;">{d_completed}</td>
                    <td style="padding:7px 10px; font-size:12px; color:#b91c1c; border-bottom:1px solid #f1f5f9; text-align:center;">{d_failed}</td>
                    <td style="padding:7px 10px; font-size:12px; color:#b45309; border-bottom:1px solid #f1f5f9; text-align:center;">{d_submitted}</td>
                    <td style="padding:7px 10px; border-bottom:1px solid #f1f5f9; text-align:center;">
                        <span style="font-size:11px; font-weight:600; color:{d_rate_color};">{d_rate}%</span>
                    </td>
                </tr>
                """

            day_wise_section = f"""
            <div style="margin-top:24px;">
                <h3 style="font-size:13px; font-weight:600; color:#374151; margin:0 0 10px 0; text-transform:uppercase; letter-spacing:0.5px;">
                    Day-wise Breakdown
                </h3>
                <table style="width:100%; border-collapse:collapse; background:#fff; border:1px solid #e5e7eb; border-radius:8px; overflow:hidden;">
                    <thead>
                        <tr style="background:#f8fafc;">
                            <th style="padding:7px 10px; font-size:11px; color:#9ca3af; text-align:left; font-weight:600;">Date</th>
                            <th style="padding:7px 10px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">Total</th>
                            <th style="padding:7px 10px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">✓</th>
                            <th style="padding:7px 10px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">✗</th>
                            <th style="padding:7px 10px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">Pending</th>
                            <th style="padding:7px 10px; font-size:11px; color:#9ca3af; text-align:center; font-weight:600;">Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        {dw_rows}
                    </tbody>
                </table>
            </div>
            """

        # ---- Action needed section (weekly reports only) ----
        action_section = ""
        if report_type == "weekly" and action_items:
            action_html = ""
            for item in action_items:
                details_li = "".join(f'<li style="font-size:12px; color:#374151; margin-bottom:3px;">{d}</li>' for d in item["details"])
                action_html += f"""
                <div style="margin-bottom:12px;">
                    <div style="font-size:12px; font-weight:600; color:#92400e; margin-bottom:4px;">{item['label']}</div>
                    <ul style="margin:0; padding-left:18px;">
                        {details_li}
                    </ul>
                </div>
                """

            action_section = f"""
            <div style="margin-top:24px;">
                <h3 style="font-size:13px; font-weight:600; color:#92400e; margin:0 0 10px 0; text-transform:uppercase; letter-spacing:0.5px;">
                    ⚠ Action Needed
                </h3>
                <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:14px 18px;">
                    {action_html}
                </div>
            </div>
            """

        dashboard_html = f"""
        <!-- STATUS BADGE -->
        <div style="display:inline-block; background:{status_color}1a; border:1px solid {status_color}40; border-radius:6px; padding:5px 12px; margin-bottom:16px;">
            <span style="font-size:13px; font-weight:600; color:{status_color};">{status_icon} {status_label}</span>
        </div>

        <!-- METRIC CARDS -->
        {cards_html}

        <!-- RATE BAR -->
        {rate_bar_html}

        <!-- FILE TYPE -->
        {file_type_html}

        <!-- FAILURE BREAKDOWN -->
        {failure_section}

        <!-- BANK DISTRIBUTION -->
        {bank_section}

        <!-- DAY-WISE (WEEKLY ONLY) -->
        {day_wise_section}

        <!-- ACTION NEEDED (WEEKLY ONLY) -->
        {action_section}
        """

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background:#f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9; padding:24px 0;">
<tr><td>
<table width="640" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto;">

    <!-- HEADER -->
    <tr>
        <td style="background:#0f172a; border-radius:12px 12px 0 0; padding:24px 32px;">
            <div style="font-size:11px; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">CreditOS Automation</div>
            <div style="font-size:20px; font-weight:700; color:#ffffff;">{title}</div>
            <div style="font-size:13px; color:#94a3b8; margin-top:4px;">Period: {period_label}</div>
        </td>
    </tr>

    <!-- BODY -->
    <tr>
        <td style="background:#ffffff; padding:28px 32px;">

            <p style="font-size:14px; color:#374151; margin:0 0 20px 0;">Hi Team,</p>

            {dashboard_html}

            <!-- DIVIDER -->
            <hr style="border:none; border-top:1px solid #e5e7eb; margin:28px 0;">

            <div style="background:#eff6ff; border-left:3px solid #3b82f6; border-radius:0 6px 6px 0; padding:10px 14px;">
                <span style="font-size:12px; color:#1d4ed8;"><strong>Note:</strong> All metrics are calculated at request level (tracking ID). The <strong>Standard Excel</strong> attachment contains the full dataset for detailed analysis.</span>
            </div>

        </td>
    </tr>

    <!-- FOOTER -->
    <tr>
        <td style="background:#f8fafc; border-top:1px solid #e5e7eb; border-radius:0 0 12px 12px; padding:16px 32px;">
            <p style="font-size:12px; color:#9ca3af; margin:0;">
                This is an automated report generated by CreditOS.<br>
                <strong style="color:#64748b;">CreditOS Team</strong>
            </p>
        </td>
    </tr>

</table>
</td></tr>
</table>

</body>
</html>"""