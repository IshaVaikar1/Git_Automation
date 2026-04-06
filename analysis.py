from collections import defaultdict
from datetime import datetime


def analyze_data(api_results):
    records = api_results.get("usageReport", {}).get("data", {}).get("data", [])

    # ---- Filter: only BSA-related records (skip FSA/RECEIVED with no files) ----
    clean_records = []
    
    FORBIDDEN_BANKS = {
        "citizens cooperative bank", "ab bank", "parner coop bank",
        "aditya bank", "makarand bank", "model test 1"
    }

    for r in records:
        tracking_id = r.get("trackingId") or r.get("tracking_id")
        if not tracking_id:
            continue
        # Skip FSA uploads (not BSA)
        if r.get("inputDocumentType") in {"FSA", "STATEMENT_OF_INCOME", "ITR",
                                           "BALANCE_SHEET", "PROFIT_AND_LOSS"}:
            continue
        
        bank_name = str(r.get("bankName") or "").strip().lower()
        if bank_name in FORBIDDEN_BANKS:
            continue

        clean_records.append(r)

    total = len(clean_records)

    completed = 0
    failed = 0
    submitted = 0

    failure_reasons = defaultdict(int)
    bank_stats = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0})
    hourly_pattern = defaultdict(int)
    day_wise = defaultdict(lambda: {"total": 0, "completed": 0, "failed": 0, "submitted": 0})

    file_type_analysis = {
        "bank_requests": 0,
        "summarized_bsa_requests": 0,
    }

    # Track failed records for inline email display
    failed_records = []

    for row in clean_records:
        files = row.get("files") or []

        status_raw = str(row.get("status") or "").strip()
        message = str(row.get("messageDetails") or "").strip()
        bank = str(row.get("bankName") or "").strip()
        tracking_id = row.get("trackingId") or row.get("tracking_id") or ""

        # ---- Robust status detection ----
        status_lower = status_raw.lower()
        message_lower = message.lower()

        is_completed = (
            status_lower == "completed"
            or (status_lower not in {"failed", "submitted", "received", "processing"}
                and message_lower == "success")
        )

        is_failed = (
            status_lower == "failed"
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

        # ---- Bank Stats (skip blank banks) ----
        valid_bank = bank and bank.lower() not in {"null", "none"}
        if valid_bank:
            bank_stats[bank]["total"] += 1
            if is_completed:
                bank_stats[bank]["success"] += 1
            elif is_failed:
                bank_stats[bank]["failed"] += 1

        # ---- Failure Intelligence (from file-level messages) ----
        failure_reason = ""
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
            failure_reason = str(reason)

            # Collect failed record details
            created_at = row.get("createdAt") or row.get("created_at") or ""
            failed_records.append({
                "tracking_id": tracking_id,
                "bank_name": bank or "N/A",
                "reason": failure_reason,
                "timestamp": _utc_to_ist_str(created_at),
            })

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

                # Day-wise breakdown
                ist_date = _utc_to_ist_date(created_at)
                if ist_date:
                    day_wise[ist_date]["total"] += 1
                    if is_completed:
                        day_wise[ist_date]["completed"] += 1
                    elif is_failed:
                        day_wise[ist_date]["failed"] += 1
                    else:
                        day_wise[ist_date]["submitted"] += 1
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

    # ---- Action Items (for weekly reports) ----
    action_items = _compute_action_items(failure_reasons, bank_stats, failed)

    return {
        "file_type_analysis": file_type_analysis,
        "system_health": system_health,
        "failure_intelligence": dict(sorted(failure_reasons.items(), key=lambda x: -x[1])),
        "bank_distribution": dict(bank_stats),
        "time_pattern": dict(sorted(hourly_pattern.items())),
        "day_wise_breakdown": dict(sorted(day_wise.items())),
        "failed_records": failed_records,
        "action_items": action_items,
    }


def _utc_to_ist_str(ts):
    """Convert UTC timestamp string to IST readable string."""
    if not ts:
        return "N/A"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        from datetime import timedelta
        ist = dt + timedelta(hours=5, minutes=30)
        return ist.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


def _utc_to_ist_date(ts):
    """Convert UTC timestamp to IST date string (YYYY-MM-DD)."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        from datetime import timedelta
        ist = dt + timedelta(hours=5, minutes=30)
        return ist.strftime("%Y-%m-%d")
    except Exception:
        return None


def _compute_action_items(failure_reasons, bank_stats, total_failed):
    """Identify areas needing attention."""
    items = []

    # Recurring failures (reasons appearing 3+ times)
    recurring = {k: v for k, v in failure_reasons.items() if v >= 3}
    if recurring:
        top = sorted(recurring.items(), key=lambda x: -x[1])[:3]
        items.append({
            "type": "recurring_failures",
            "label": "Recurring Failure Patterns",
            "details": [f"{reason} ({count} occurrences)" for reason, count in top],
        })

    # Most affected banks (failure rate > 30% and at least 2 failures)
    affected_banks = []
    for bank, stats in bank_stats.items():
        b_total = stats.get("total", 0)
        b_failed = stats.get("failed", 0)
        if b_total > 0 and b_failed >= 2:
            rate = round((b_failed / b_total) * 100, 1)
            if rate > 30:
                affected_banks.append(f"{bank} — {rate}% failure rate ({b_failed}/{b_total})")

    if affected_banks:
        items.append({
            "type": "affected_banks",
            "label": "Banks Requiring Attention",
            "details": affected_banks[:5],
        })

    return items