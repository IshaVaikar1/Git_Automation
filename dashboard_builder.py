import json
import os
from datetime import datetime

def build_dashboard(data_list, report_type, startDate, endDate, filename):
    """
    Generates a high-performance, compact, and professional HTML dashboard.
    Optimized for speed and minimal scrolling.
    """
    
    # Process data efficiently
    status_counts = {"Completed": 0, "failed": 0, "submitted": 0}
    bank_agg = {}
    
    formatted_data = []
    for item in data_list:
        raw_status = str(item.get("status", "")).lower()
        bank = item.get("bank_name") or item.get("bank") or "Unknown"
        
        status = "submitted"
        if any(x in raw_status for x in ["fail", "error", "reject", "terminate"]):
            status = "failed"
        elif any(x in raw_status for x in ["complete", "success", "done"]):
            status = "Completed"
            
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Aggregate bank data for a simple chart
        if bank not in bank_agg:
            bank_agg[bank] = {"total": 0, "success": 0}
        bank_agg[bank]["total"] += 1
        if status == "Completed":
            bank_agg[bank]["success"] += 1
            
        formatted_data.append([
            item.get("tracking_id") or "N/A",
            bank,
            status,
            item.get("file_type", "N/A"),
            item.get("created_at") or item.get("timestamp") or "N/A"
        ])

    # Sort bank statistics by volume
    top_banks = sorted(bank_agg.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
    bank_labels = [x[0] for x in top_banks]
    bank_volumes = [x[1]['total'] for x in top_banks]
    bank_success = [round((x[1]['success']/x[1]['total'])*100, 1) if x[1]['total'] > 0 else 0 for x in top_banks]

    total = len(data_list)
    success_rate = round((status_counts["Completed"] / total * 100), 1) if total > 0 else 0

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BSA Report Dashboard | {startDate}</title>
    <link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f4f7f9; color: #333; margin: 0; padding: 20px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
        .header h1 {{ margin: 0; font-size: 20px; color: #1a202c; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }}
        .card {{ background: #fff; padding: 15px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
        .card-label {{ font-size: 12px; color: #718096; font-weight: 600; text-transform: uppercase; }}
        .card-value {{ font-size: 24px; font-weight: 700; margin-top: 5px; }}
        .main-content {{ display: grid; grid-template-columns: 1fr 350px; gap: 20px; }}
        .chart-container {{ height: 250px; position: relative; }}
        .table-area {{ background: #fff; padding: 15px; border-radius: 6px; border: 1px solid #e2e8f0; }}
        table.dataTable td {{ font-size: 13px; padding: 8px !important; }}
        table.dataTable th {{ font-size: 12px; background: #f8fafc !important; }}
        .status-badge {{ padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
        .status-Completed {{ background: #c6f6d5; color: #22543d; }}
        .status-failed {{ background: #fed7d7; color: #822727; }}
        .status-submitted {{ background: #feebc8; color: #744210; }}
    </style>
</head>
<body>

<div class="header">
    <h1>BSA Insights Dashboard — <span style="font-weight:400; color:#667">{startDate} to {endDate}</span></h1>
    <div style="font-size:12px; color:#667">High-Performance View ({total} records)</div>
</div>

<div class="summary-grid">
    <div class="card">
        <div class="card-label">Total Requests</div>
        <div class="card-value">{total}</div>
    </div>
    <div class="card">
        <div class="card-label">Success Rate</div>
        <div class="card-value" style="color:#2f855a">{success_rate}%</div>
    </div>
    <div class="card">
        <div class="card-label">Failures</div>
        <div class="card-value" style="color:#c53030">{status_counts['failed']}</div>
    </div>
    <div class="card">
        <div class="card-label">Avg. Volume/Hr</div>
        <div class="card-value">{round(total/24, 1)}</div>
    </div>
</div>

<div class="main-content">
    <div class="table-area">
        <table id="mainTable" class="display compact" style="width:100%">
            <thead>
                <tr>
                    <th>Tracking ID</th>
                    <th>Bank Name</th>
                    <th>Status</th>
                    <th>Request Type</th>
                    <th>Created At</th>
                </tr>
            </thead>
        </table>
    </div>

    <div class="card">
        <div class="card-label" style="margin-bottom:15px">Top Banks Performance</div>
        <div class="chart-container">
            <canvas id="bankChart"></canvas>
        </div>
        <div style="margin-top:20px; font-size:11px; color:#718096; line-height:1.4">
            * Sorting: Showing top 10 banks by volume. <br>
            * Legend: Blue bars show total volume, Green dots show success %.
        </div>
    </div>
</div>

<script>
    const tableData = {json.dumps(formatted_data)};

    $(document).ready(function() {{
        $('#mainTable').DataTable({{
            data: tableData,
            pageLength: 20,
            deferRender: true,
            scrollY: '500px',
            scrollCollapse: true,
            order: [[4, 'desc']],
            columns: [
                {{ title: "Tracking ID" }},
                {{ title: "Bank Name" }},
                {{ 
                    title: "Status",
                    render: function(data) {{
                        return `<span class="status-badge status-${{data}}">${{data}}</span>`;
                    }}
                }},
                {{ title: "Request Type" }},
                {{ title: "Created At" }}
            ]
        }});

        new Chart(document.getElementById('bankChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(bank_labels)},
                datasets: [
                    {{
                        label: 'Volume',
                        data: {json.dumps(bank_volumes)},
                        backgroundColor: '#bee3f8',
                        order: 2
                    }},
                    {{
                        label: 'Success %',
                        data: {json.dumps(bank_success)},
                        borderColor: '#2f855a',
                        type: 'line',
                        yAxisID: 'y1',
                        order: 1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ display: false }} }},
                    y1: {{ beginAtZero: true, position: 'right', max: 100, grid: {{ display: false }} }}
                }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
    }});
</script>

</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    return filename
