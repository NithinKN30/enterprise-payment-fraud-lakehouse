
from typing import Any


def detect_fraud(transaction: dict[str, Any]) -> list[str]:
    """
    Apply basic rule-based checks to a transaction.
    Returns a list of reasons why it may be suspicious.
    """

    reasons = []

    amount = float(transaction.get("transaction_amount", 0))
    status = str(transaction.get("status", "")).upper()

    # Rule 1: High-value transaction
    if amount >= 10000:
        reasons.append("High-value transaction")

    # Rule 2: Failed transaction
    if status == "FAILED":
        reasons.append("Failed transaction")

    # Rule 3: Unusually large transaction
    if amount >= 50000:
        reasons.append("Very high transaction amount")

    return reasons
