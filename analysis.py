from collections import defaultdict
from datetime import datetime

def analyze_data(api_results):
    records = api_results.get("usageReport", {}).get("data", {}).get("data", [])

    # ---- Clean records (keep valid tracking ids only) ----
    clean_records = [
        r for r in records
        if r.get("trackingId") or r.get("tracking_id")
    ]

    total = len(clean_records)

    completed = 0
    failed = 0
    submitted = 0

    failure_reasons = defaultdict(int)
    bank_stats = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})
    hourly_pattern = defaultdict(int)

    file_type_analysis = {
        "bank_requests": 0,
        "summarized_bsa_requests": 0,
    }

    for row in clean_records:
        files = row.get("files") or []
        file_count = len(files)

        status_raw = str(row.get("status") or "").strip().lower()
        message = str(row.get("messageDetails") or "").strip().lower()
        bank = str(row.get("bankName") or "").strip()

        # ---- Skip invalid banks ONLY for bank stats ----
        valid_bank = True
        if not bank or bank.lower() in ["null", "none"]:
            valid_bank = False

        # ---- Robust status detection ----
        is_completed = (
            status_raw in ["completed", "success"]
            or message == "success"
        )

        is_failed = (
            status_raw in ["failed", "error"]
            or "fail" in message
        )

        # ---- System Health ----
        if is_completed:
            completed += 1
        elif is_failed:
            failed += 1
        else:
            submitted += 1

        # ---- Bank Stats (only if valid bank) ----
        if valid_bank:
            bank_stats[bank]["total"] += 1

            if is_completed:
                bank_stats[bank]["success"] += 1
            elif is_failed:
                bank_stats[bank]["failed"] += 1

        # ---- Failure Intelligence ----
        if is_failed:
            reason = "Unknown"

            if files:
                file_obj = files[0] or {}
                reason = (
                    file_obj.get("statusMessage")
                    or file_obj.get("fileStatus")
                    or row.get("messageDetails")
                    or "Unknown"
                )

            failure_reasons[reason] += 1

        # ---- File Type Analysis (request level) ----
        if file_count == 1:
            file_type_analysis["bank_requests"] += 1
        elif file_count > 1:
            file_type_analysis["summarized_bsa_requests"] += 1

        # ---- Time Pattern ----
        created_at = row.get("createdAt") or row.get("created_at")
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                hourly_pattern[dt.hour] += 1
            except Exception:
                pass

    # ---- System Health Summary ----
    system_health = {
        "total": total,
        "Completed": completed,
        "failed": failed,
        "submitted": submitted,
        "success_rate": round((completed / total) * 100, 2) if total else 0,
        "failure_rate": round((failed / total) * 100, 2) if total else 0,
    }

    return {
        "file_type_analysis": file_type_analysis,
        "system_health": system_health,
        "failure_intelligence": dict(sorted(failure_reasons.items(), key=lambda x: -x[1])),
        "bank_distribution": dict(bank_stats),
        "time_pattern": dict(sorted(hourly_pattern.items()))
    }