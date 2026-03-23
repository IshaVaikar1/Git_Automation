# admin_body.py

def admin_failure_message(failures, timestamp, summary=""):

    msg = f"""
<html>
<body>

<p>Hello Admin,</p>

<p>The automated report <b>FAILED</b>.</p>

<p><b>Failure Summary:</b><br>
{summary}
</p>
<p><b>Errors Detected:</b></p>
<ul>
"""
    for name, err in failures:
        msg += f"<li>{name}: {err}</li>"

    msg += f"""
</ul>
<p>
This email contains:<br>
- error.log only (Excel not generated)
</p>

<p><b>Timestamp:</b> {timestamp}</p>

<p>
Thanks and Regards,<br>
CreditOS Team
</p>

</body>
</html>
"""
    return msg


def workflow_failure_message(failures, timestamp, summary=""):

    msg = f"""
<html>
<body>

<p>Hello Admin,</p>

<p>The automated report <b>FAILED</b> due to workflow failure.</p>

<p><b>Failure Summary:</b><br>
{summary}
</p>

<p><b>Errors Detected:</b></p>
<ul>
"""

    for name, err in failures:
        msg += f"<li>{name}: {err}</li>"

    msg += f"""
</ul>

<p>
This email contains:<br>
- error.log only (Excel not generated)
</p>

<p><b>Timestamp:</b> {timestamp}</p>

<p>
Thanks and Regards,<br>
CreditOS Team
</p>

</body>
</html>
"""
    return msg

