import csv
import random
import argparse
from pathlib import Path
transactions = [
    {
        "transaction_id": "TXN100001",
        "customer_id": "CUST1001",
        "merchant_id": "MERCH201",
        "transaction_timestamp": "2026-10-13 10:15:30",
        "transaction_amount": 1250.75,
        "currency": "INR",
        "payment_method": "UPI",
        "transaction_type": "PURCHASE",
        "country": "IN",
        "device_id": "DEV5001",
        "status": "SUCCESS",
    },
    {
        "transaction_id": "TXN100002",
        "customer_id": "CUST1002",
        "merchant_id": "MERCH202",
        "transaction_timestamp": "2026-10-13 10:16:10",
        "transaction_amount": 4999.00,
        "currency": "INR",
        "payment_method": "CARD",
        "transaction_type": "PURCHASE",
        "country": "IN",
        "device_id": "DEV5002",
        "status": "FAILED",
    },
]

output_dir = Path("datasets/raw")
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "transactions.csv"

with output_file.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=transactions[0].keys())
    writer.writeheader()
    writer.writerows(transactions)
    
print(f"Generated {len(transactions)} transactions and saved to {output_file}")
