from collections import defaultdict
from datetime import datetime


def analyze_data(api_results):
    records = api_results.get("usageReport", {}).get("data", {}).get("data", [])

    # ---- Filter: only BSA-related records (skip FSA/RECEIVED with no files) ----
    clean_records = []
    for r in records:
        tracking_id = r.get("trackingId") or r.get("tracking_id")
        if not tracking_id:
            continue
        # Skip FSA uploads (not BSA)
        if r.get("inputDocumentType") in {"FSA", "STATEMENT_OF_INCOME", "ITR",
                                           "BALANCE_SHEET", "PROFIT_AND_LOSS"}:
            continue
        clean_records.append(r)

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

    FORBIDDEN_BANKS = {
        "citizens cooperative bank", "ab bank", "parner coop bank",
        "aditya bank", "makarand bank"
    }

    for row in clean_records:
        files = row.get("files") or []
        file_count = len(files)

        status_raw = str(row.get("status") or "").strip()
        message = str(row.get("messageDetails") or "").strip()
        bank = str(row.get("bankName") or "").strip()

        # ---- Robust status detection (case-aware, matches real API values) ----
        status_lower = status_raw.lower()
        message_lower = message.lower()

        is_completed = (
            status_lower in {"completed"}
            or message_lower == "success"
        )

        is_failed = (
            status_lower in {"failed"}
            or "fail" in status_lower
        )

        is_submitted = status_lower in {"submitted", "received", "processing"}

        # ---- System Health ----
        if is_completed:
            completed += 1
        elif is_failed:
            failed += 1
        else:
            submitted += 1

        # ---- Bank Stats (skip forbidden / blank banks) ----
        valid_bank = bank and bank.lower() not in {"null", "none"} and \
                     bank.lower() not in FORBIDDEN_BANKS
        if valid_bank:
            bank_stats[bank]["total"] += 1
            if is_completed:
                bank_stats[bank]["success"] += 1
            elif is_failed:
                bank_stats[bank]["failed"] += 1

        # ---- Failure Intelligence (from file-level messages) ----
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
                # Normalize duplicates
                if reason and reason.lower() in {"failed", "success", ""}:
                    reason = row.get("messageDetails") or "Unknown"
            failure_reasons[str(reason)] += 1

        # ---- File Type Analysis (request level) ----
        bsa_files = [f for f in files if f.get("documentType") == "BANK"]
        summ_files = [f for f in files if f.get("documentType") == "SUMMARIZED_BSA"]

        if summ_files:
            file_type_analysis["summarized_bsa_requests"] += 1
        elif bsa_files:
            file_type_analysis["bank_requests"] += 1

        # ---- Time Pattern (IST offset +5:30) ----
        created_at = row.get("createdAt") or row.get("created_at")
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                ist_hour = (dt.hour + 5) % 24 + (1 if dt.minute >= 30 else 0)
                ist_hour = ist_hour % 24
                hourly_pattern[ist_hour] += 1
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