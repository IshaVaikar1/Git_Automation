
# report_parent.py
import os
import json
from datetime import datetime, date, timedelta, timezone
from api_client import call_api
from api_config import API_FLOW_CONFIG
from excel_builder import build_excel
from email_sender import send_email
from error_handler import init_logger
from success_body import success_message
from failure_body import failure_message
from admin_body import admin_failure_message, workflow_failure_message


# ---- ENV VARIABLES (GitHub Secrets / Workflow Inputs) ----
BASE_URL = os.getenv("BASE_URL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

HEADER_NAME = os.getenv("HEADER_NAME")
HEADER_VALUE = os.getenv("HEADER_VALUE")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
RECIPIENTS_EMAILS = os.getenv("RECIPIENTS_EMAILS")

MODE = os.getenv("MODE")
EMAILS = os.getenv("EMAILS")

START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")

REPORT_TYPE = os.getenv("REPORT_TYPE", "daily")


def validate_iso_date(value: str, var_name: str):
    if not value:
        return

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"{var_name} must be in ISO format YYYY-MM-DD. Got: {value}"
        )

def validate_date_range(startDate, endDate):
    if startDate and endDate:
        s = datetime.strptime(startDate, "%Y-%m-%d").date()
        e = datetime.strptime(endDate, "%Y-%m-%d").date()

        if s > e:
            raise ValueError(
                f"START_DATE ({startDate}) cannot be after END_DATE ({endDate})"
            )


logger = init_logger()

def load_dynamic_api_flow():
    api_flow = []
    base_url = BASE_URL
    

    if not base_url:
        raise RuntimeError("BASE_URL is missing in GitHub secrets")

    for cfg in API_FLOW_CONFIG:
        url = base_url.rstrip("/") + cfg["endpoint"]

        step = {
            "name": cfg["name"],
            "method": cfg["method"],
            "url": url,
            "body": cfg.get("body", {}),
            "params": cfg.get("params", {}),
            "headers": cfg.get("headers", {})
        }
        api_flow.append(step)

    return api_flow


def summarize_log_error():
    try:
        if not os.path.exists("error.log"):
            return "Run log missing."

        with open("error.log", "r", encoding="utf-8") as f:
            log = f.read()

        if "401" in log or "Unauthorized" in log:
            return "Authentication failed — invalid or expired token."
        if "ConnectionError" in log:
            return "API server unreachable — network or server down."
        if "JSONDecodeError" in log:
            return "Invalid API response — JSON parsing failed."
        if "SMTPAuthenticationError" in log:
            return "Email sending failed — SMTP authentication error."
        if "Timeout" in log:
            return "API timeout — server did not respond."
        if "FileNotFoundError" in log:
            return "Missing file — attachment or resource not found."
        if "KeyError" in log:
            return "Required field missing in API response."
        if "Token" in log and "WARNING" in log:
            return "Token missing in login API response."

        return "Unexpected workflow failure. Check error.log for details."

    except Exception:
        return "Error analyzing log file."



def pick_recipients(all_rec, mode, emails):
    if not mode:
        raise ValueError("MODE env variable is missing. Use 'all' or 'custom'.")

    mode = mode.lower().strip()
    emails = (emails or "").strip()

    if mode == "all":
        return all_rec

    if mode == "custom":
        if not emails:
            raise ValueError("For MODE=custom, EMAILS must be provided.")
        return [e.strip() for e in emails.split(",") if e.strip()]

    raise ValueError(f"Invalid MODE: {mode}. Allowed: all, custom")



def execute_api_flow(api_flow):
    results = {}
    shared = {}

    userId = ADMIN_USERNAME
    password = ADMIN_PASSWORD
    startDate = os.getenv("START_DATE")
    endDate = os.getenv("END_DATE")
    headerName = HEADER_NAME
    headerValue = HEADER_VALUE
    userAgent ="User-Agent"
    userAgentValue ="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    

    for step in api_flow:
        name = step["name"]
        method = step["method"]
        url = step["url"]
        params = step.get("params") or {}
        body = step.get("body") or {}
        headers = step.get("headers") or {}

        if isinstance(params, dict):
            params = {
                k: v.replace("{startDate}", startDate).replace("{endDate}", endDate)
                if isinstance(v, str) else v
                for k, v in params.items()
            }

        if isinstance(body, dict):
            body = {
                k: v.replace("{startDate}", startDate).replace("{endDate}", endDate)
                if isinstance(v, str) else v
                for k, v in body.items()
            }

        if isinstance(body, dict):
            body = {
                k: v.replace("{userId}", userId).replace("{password}", password)
                if isinstance(v, str) else v
                for k, v in body.items()
            }
                
               
        if not isinstance(headers, dict):
            headers = {}

        # Inject mandatory firewall bypass headers
        headers[headerName] = headerValue
        headers[userAgent] = userAgentValue

        # Replace placeholders inside existing header values
        headers = {
            k: v.replace("{headerName}", headerName)
                .replace("{headerValue}", headerValue)
                .replace("{userAgent}", userAgent)
                .replace("{userAgentValue}", userAgentValue)
            if isinstance(v, str) else v
            for k, v in headers.items()
        }
        logger.info(f"headers info'{headers}'")
        

                
        if "token" in shared:
            token = shared["token"]
            headers = {k: v.replace("{token}", token) if isinstance(v, str) else v for k, v in headers.items()}
            params = {k: v.replace("{token}", token) if isinstance(v, str) else v for k, v in params.items()}

        try:
            resp = call_api(method=method, url=url, params=params, body=body, headers=headers)
        except Exception:
            logger.error(f"[API ERROR] Step '{name}' failed while calling {url}", exc_info=True)
            raise

        results[name] = resp
        logger.info(f"[RESPONSE] Step '{name}' returned: {resp}")

        if isinstance(resp, dict):
            if "accessToken" in resp:
                shared["token"] = resp["accessToken"]
            elif "access_token" in resp:
                shared["token"] = resp["access_token"]
            elif "token" in resp:
                shared["token"] = resp["token"]
            elif "data" in resp and "tokens" in resp["data"]:
                shared["token"] = resp["data"]["tokens"]["accessToken"]

    for api_name, resp in results.items():
        if isinstance(resp, str) and "," in resp:
            path = f"{api_name}.csv"
            with open(path, "w", encoding="utf-8") as f:
                f.write(resp)
            results[api_name] = path

    return results
def resolve_date_range():
    """
    Resolves start_date and end_date based on REPORT_TYPE.
    Supports only: daily, weekly
    """

    report_type = REPORT_TYPE.lower()

    # If explicitly provided, respect them
    startDate = os.getenv("START_DATE")
    endDate = os.getenv("END_DATE")

    if startDate and endDate:
        return startDate, endDate

    yesterday = date.today() - timedelta(days=1)

    if report_type == "daily":
        d = yesterday
        return d.isoformat(), d.isoformat()

    if report_type == "weekly":
        end = yesterday
        start = yesterday - timedelta(days=6)
        return start.isoformat(), end.isoformat()

    raise ValueError("Only daily and weekly report types are supported")

def build_subject(report_type, start_date, end_date):
    if start_date != end_date:
        report_type = "range"
    report_type = report_type.lower()

    if report_type == "daily":
        return f"BSA Daily Usage Report: {start_date}"

    if report_type == "weekly":
        return f"BSA Weekly Usage Report: {start_date} to {end_date}"

    return f"BSA Usage Report: {start_date} to {end_date}"


def main():
    try:

        logger.info("==== RUN START ====")
        

        # FAIL FAST: validate dates
        validate_iso_date(os.getenv("START_DATE"), "START_DATE")
        validate_iso_date(os.getenv("END_DATE"), "END_DATE")

        validate_date_range(
            os.getenv("START_DATE"),
            os.getenv("END_DATE")
        )

        IST = timedelta(hours=5, minutes=30)
        timestamp = (datetime.now(timezone.utc) + IST).date().isoformat()

        if not ADMIN_EMAIL:
            logger.error("ADMIN_EMAIL is missing")
            return

        recipients_json = RECIPIENTS_EMAILS
        if not recipients_json:
            raise RuntimeError("RECIPIENTS_EMAILS is missing")
        recipients_json = recipients_json.strip()
        try:
            all_recipients = json.loads(recipients_json)
            if isinstance(all_recipients, str):
                all_recipients = [all_recipients]
        except json.JSONDecodeError:
            all_recipients = [e.strip() for e in recipients_json.split(",") if e.strip()]

        recipients = pick_recipients(all_recipients, MODE, EMAILS)
    
        startDate, endDate = resolve_date_range()

        if startDate != endDate:
            report_type = "range"
        else:
            report_type = (REPORT_TYPE or "daily").lower()
        subject = build_subject(report_type, startDate, endDate)
        excel_filename = subject.replace(":", "").replace(" ", "_") + ".xlsx"

        os.environ["START_DATE"] = startDate
        os.environ["END_DATE"] = endDate


        try:
            api_results = execute_api_flow(load_dynamic_api_flow())
        except Exception as e:
            summary = summarize_log_error()

            # ---- Send detailed error to admin ----
            send_email(
                SMTP_HOST,
                SMTP_PORT,
                SMTP_USER,
                SMTP_PASS,
                [ADMIN_EMAIL],
                "REPORT FAILED",
                admin_failure_message([("api_flow", str(e))], timestamp, summary),
                attachments=["error.log"],
            )

            send_email(
                SMTP_HOST,
                SMTP_PORT,
                SMTP_USER,
                SMTP_PASS,
                recipients,
                f"BSA Report Failed - {timestamp}",
                failure_message(timestamp),
                attachments=None,
            )
            return
        excel_payload = {}

        for resp in api_results.items():
            if isinstance(resp, dict) and isinstance(resp.get("data"), dict):
                # Node API structure: { message, data: { count, data: [...] } }
                inner_data = resp["data"].get("data")
                if isinstance(inner_data, list):
                    excel_payload["data"] = {"data": inner_data}
                    break

                # Fallback to original behavior if nothing matched
        if not excel_payload:
            excel_payload = api_results


        excel_path = build_excel(api_results , excel_filename)

        body = success_message(report_type, startDate, endDate)

        send_email(
            SMTP_HOST,
            SMTP_PORT,
            SMTP_USER,
            SMTP_PASS,
            recipients,
            subject,
            body,
            attachments=[excel_path],
        )

        logger.info("==== RUN COMPLETE ====")

    except Exception as e:

        logger.error("Workflow failed", exc_info=True)

        summary = summarize_log_error()

        send_email(
            SMTP_HOST,
            int(SMTP_PORT or "587"),
            SMTP_USER,
            SMTP_PASS,
            [ADMIN_EMAIL],
            "REPORT FAILED (ADMIN ALERT)",
            workflow_failure_message([("workflow", str(e))], timestamp, summary),
            attachments=["error.log"],
        )

if __name__ == "__main__":
    main()
