def success_message(report_type, start_date, end_date):
    
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

    return f"""
<p>Hi Team,</p>

<p>
Please find the attached <b>{title}</b> {date_text}.
</p>

<p>
This report includes details of each analysis execution with the following columns: 
</p>


<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; border:1px solid #d0d0d0;">
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
<a href="https://cofinitysystems-my.sharepoint.com/:x:/g/personal/tamanash_malkhandi_creditos_in/IQDda3ROiyyUQJ5_aANM4SNAAVW6plpbFuO-j-MYaiXGFUc">Bank Details Excel Sheet</a>
</p>

<p>
Thanks and Regards,<br>
CreditOS Team
</p>
"""