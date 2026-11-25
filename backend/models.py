from dataclasses import dataclass


@dataclass
class Transaction:
    transaction_id: str
    customer_id: str
    merchant_id: str
    transaction_timestamp: str
    transaction_amount: float
    currency: str
    payment_method: str
    transaction_type: str
    country: str
    device_id: str
    status: str

    @classmethod
    def from_csv_row(cls, row: dict) -> "Transaction":
        return cls(
            transaction_id=row["transaction_id"],
            customer_id=row["customer_id"],
            merchant_id=row["merchant_id"],
            transaction_timestamp=row["transaction_timestamp"],
            transaction_amount=float(row["transaction_amount"]),
            currency=row["currency"],
            payment_method=row["payment_method"],
            transaction_type=row["transaction_type"],
            country=row["country"],
            device_id=row["device_id"],
            status=row["status"],
        )