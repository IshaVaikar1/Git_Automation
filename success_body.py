def success_message(report_type, start_date, end_date, analysis=None):
    
    report_type = report_type.lower()

    if report_type == "daily":
        title = "BSA Daily Usage Report"
        date_text = f"for <b>{start_date}</b>"

    elif report_type == "weekly":
        title = "BSA Weekly Usage Report"
        date_text = f"for the period from <b>{start_date}</b> to <b>{end_date}</b>"

    else:
        title = "BSA Usage Report"
        date_text = f"for the period from <b>{start_date}</b> to <b>{end_date}</b>"

    # ---- ANALYSIS BLOCK ----
    analysis_html = ""

    if analysis:
        sh = analysis.get("system_health", {})
        failures = analysis.get("failure_intelligence", {})
        banks = analysis.get("bank_distribution", {})
        hours = analysis.get("time_pattern", {})
        fta = analysis.get("file_type_analysis", {})

        # ---- CARDS ----
        cards_html = f"""
        <div style="display:flex; gap:10px; margin-bottom:20px;">
            <div style="flex:1; background:#f5f5f5; padding:10px; border-radius:8px;">
                <b>Total</b><br>{sh.get("total", 0)}
            </div>
            <div style="flex:1; background:#e8f5e9; padding:10px; border-radius:8px;">
                <b>Completed</b><br>{sh.get("Completed", 0)}
            </div>
            <div style="flex:1; background:#ffebee; padding:10px; border-radius:8px;">
                <b>Failed</b><br>{sh.get("failed", 0)}
            </div>
            <div style="flex:1; background:#fff3e0; padding:10px; border-radius:8px;">
                <b>Submitted</b><br>{sh.get("submitted", 0)}
            </div>
        </div>
        """

        # ---- PROGRESS BARS ----
        success_rate = sh.get("success_rate", 0)
        failure_rate = sh.get("failure_rate", 0)

        bars_html = f"""
        <div style="margin-bottom:20px;">
            <b>Success Rate ({success_rate}%)</b>
            <div style="background:#eee; border-radius:6px;">
                <div style="width:{success_rate}%; background:#4caf50; padding:6px 0;"></div>
            </div>

            <br>

            <b>Failure Rate ({failure_rate}%)</b>
            <div style="background:#eee; border-radius:6px;">
                <div style="width:{failure_rate}%; background:#f44336; padding:6px 0;"></div>
            </div>
        </div>
        """

        file_type_html = f"""
        <h3>File Type Analysis</h3>
        <div style="display:flex; gap:10px; margin-bottom:20px;">

            <div style="flex:1; background:#e3f2fd; padding:10px; border-radius:8px;">
                <b>Bank Requests</b><br>{fta.get('bank_requests', 0)}
            </div>

            <div style="flex:1; background:#f3e5f5; padding:10px; border-radius:8px;">
                <b>Summarized Requests</b><br>{fta.get('summarized_bsa_requests', 0)}
            </div>

        </div>
        """

        # ---- BAR CHART BUILDER ----
        def build_bar_chart(data):
            if not data:
                return ""

            max_val = max(v.get("total", 0) for v in data.values())
            rows = ""

            for key, val in data.items():
                width = int((val["total"] / max_val) * 200)

                rows += f"""
                <div style="display:flex; align-items:center; margin:5px 0;">
                    <div style="width:140px;">{key}</div>
                    <div style="background:#2196f3; height:14px; width:{width}px;"></div>
                    <div style="margin-left:8px;">{val['total']}</div>
                </div>
                """

            return rows

        # ---- BANK CHART ----
        bank_chart_html = build_bar_chart(banks)

        # ---- TIME CHART ----
        time_chart_html = ""
        if hours:
            max_val = max(hours.values())
            for hour, count in hours.items():
                width = int((count / max_val) * 200)
                time_chart_html += f"""
                <div style="display:flex; align-items:center; margin:5px 0;">
                    <div style="width:80px;">{hour}:00</div>
                    <div style="background:#9c27b0; height:14px; width:{width}px;"></div>
                    <div style="margin-left:8px;">{count}</div>
                </div>
                """

        # ---- FAILURE LIST ----
        failure_html = "<ul>"
        for k, v in list(failures.items())[:5]:
            failure_html += f"<li>{k}: {v}</li>"
        failure_html += "</ul>"

        # ---- FINAL ANALYSIS ----
        analysis_html = f"""
        <h3>System Health Overview</h3>
        {cards_html}
        {bars_html}

        {file_type_html}

        <h3>Failure Intelligence</h3>
        {failure_html}

        <h3>Bank-wise Load Distribution</h3>
        {bank_chart_html}

        <h3>Time-based Load Pattern</h3>
        {time_chart_html}
        """

    return f"""
<p>Hi Team,</p>

<p>
Please find the attached <b>{title}</b> {date_text}.
</p>

{analysis_html}

<p>
This report includes details of each analysis execution with the following columns:
</p>

<p style="background:#eef5ff; padding:10px; border-radius:6px;">
<b>Note:</b> All metrics in this report are calculated at request level (tracking ID).
</p>
<table border="1" cellpadding="8" cellspacing="0" 
style="border-collapse: collapse; width: 100%; border:1px solid #d0d0d0;">

<tr style="background-color:#f2f2f2;">
<th align="left">Column Name</th>
<th align="left">Description</th>
</tr>

<tr><td>bank_name</td><td>Name of the bank</td></tr>
<tr><td>tracking_id</td><td>Unique tracking identifier for the request</td></tr>
<tr><td>process_id</td><td>Unique identifier for the processing workflow</td></tr>
<tr><td>file_id</td><td>Unique identifier for the uploaded file</td></tr>
<tr><td>file_doc_type</td><td>Document type of the uploaded file</td></tr>
<tr><td>file_type</td><td>Type/format of the file</td></tr>
<tr><td>file_status</td><td>Current processing status of the file</td></tr>
<tr><td>file_created_at</td><td>File creation timestamp</td></tr>
<tr><td>file_updated_at</td><td>Last updated timestamp for the file</td></tr>
<tr><td>status_msg</td><td>Status message returned by the processing system</td></tr>
<tr><td>status_code</td><td>Status code returned by the processing system</td></tr>

</table>

<p style="margin-top:15px;">
Along with this report, a separate Excel sheet containing Bank Details has been shared through the link below:
</p>

<p>
<a href="https://cofinitysystems-my.sharepoint.com/:x:/g/personal/tamanash_malkhandi_creditos_in/IQDda3ROiyyUQJ5_aANM4SNAAVW6plpbFuO-j-MYaiXGFUc">
Bank Details Excel Sheet
</a>
</p>

<p>
Thanks and Regards,<br>
CreditOS Team
</p>
"""