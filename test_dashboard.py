import sys
import os
import random
from datetime import datetime, timedelta

# Add current dir to path
sys.path.append(os.getcwd())

from dashboard_builder import build_dashboard

def generate_mock_data(count=1000):
    banks = ["HDFC Bank", "ICICI Bank", "Axis Bank", "State Bank of India", "Kotak Mahindra Bank", "Bank of Baroda"]
    statuses = ["completed", "failed", "submitted"]
    file_types = ["bank_requests", "summarized_bsa_requests"]
    
    data = []
    base_time = datetime.now() - timedelta(days=1)
    
    for i in range(count):
        bank = random.choice(banks)
        status = random.choice(statuses)
        if random.random() < 0.85: # 85% success
            status = "completed"
        elif random.random() < 0.5:
            status = "failed"
        
        # Add some random hour
        ts = base_time + timedelta(minutes=random.randint(0, 1440))
        
        data.append({
            "tracking_id": f"TRK-2026-{100000 + i}",
            "bank_name": bank,
            "status": status,
            "file_type": random.choice(file_types),
            "created_at": ts.isoformat() + "Z"
        })
    return data

if __name__ == "__main__":
    print("Generating 1,000 mock records...")
    mock_data = generate_mock_data(1000)
    
    print("Building dashboard...")
    output_file = "/home/user/Desktop/githubAutomation/Git_Automation/digital_dashboard_preview.html"
    build_dashboard(mock_data, "daily", "2026-04-01", "2026-04-01", output_file)
    
    print(f"✓ Dashboard generated: {output_file}")
