import csv
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.fraud_rules import detect_fraud

from fastapi import FastAPI, HTTPException, Query

from backend.database import get_connection, initialize_database
from backend.models import Transaction


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "datasets" / "raw" / "transactions.csv"

app = FastAPI(
    title="Payment Fraud Monitoring API",
    description="API for monitoring and analyzing payment transactions",
    version="1.0.0",
)
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR / "static"),
    name="static",
)
@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(FRONTEND_DIR / "index.html")


def load_transactions_from_csv() -> int:
    initialize_database()

    connection = get_connection()
    loaded_count = 0

    try:
        with CSV_PATH.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                transaction = Transaction.from_csv_row(row)

                connection.execute(
                    """
                    INSERT OR REPLACE INTO transactions
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        transaction.transaction_id,
                        transaction.customer_id,
                        transaction.merchant_id,
                        transaction.transaction_timestamp,
                        transaction.transaction_amount,
                        transaction.currency,
                        transaction.payment_method,
                        transaction.transaction_type,
                        transaction.country,
                        transaction.device_id,
                        transaction.status,
                    ),
                )

                loaded_count += 1

        connection.commit()

    finally:
        connection.close()

    return loaded_count


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/")
def home():
    return {
        "message": "Payment Fraud Monitoring API is running",
        "version": "1.0.0",
    }


@app.get("/api/transactions")
def get_transactions(
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
):
    connection = get_connection()

    try:
        if status:
            rows = connection.execute(
                """
                SELECT * FROM transactions
                WHERE UPPER(status) = UPPER(?)
                ORDER BY transaction_timestamp DESC
                LIMIT ?
                """,
                (status, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT * FROM transactions
                ORDER BY transaction_timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


@app.get("/api/stats")
def get_stats():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT
                COUNT(*) AS total_transactions,

                COALESCE(SUM(transaction_amount), 0)
                    AS total_amount,

                COALESCE(AVG(transaction_amount), 0)
                    AS average_amount,

                SUM(
                    CASE
                        WHEN UPPER(status) = 'SUCCESS'
                        THEN 1
                        ELSE 0
                    END
                ) AS successful_transactions,

                SUM(
                    CASE
                        WHEN UPPER(status) = 'FAILED'
                        THEN 1
                        ELSE 0
                    END
                ) AS failed_transactions

            FROM transactions
            """
        ).fetchone()

        total = result["total_transactions"] or 0
        successful = result["successful_transactions"] or 0
        failed = result["failed_transactions"] or 0

        success_rate = (
            (successful / total) * 100
            if total > 0
            else 0
        )

        failure_rate = (
            (failed / total) * 100
            if total > 0
            else 0
        )

        payment_methods = connection.execute(
            """
            SELECT
                payment_method,
                COUNT(*) AS transaction_count,
                COALESCE(SUM(transaction_amount), 0)
                    AS total_amount
            FROM transactions
            GROUP BY payment_method
            ORDER BY transaction_count DESC
            """
        ).fetchall()

        statuses = connection.execute(
            """
            SELECT
                UPPER(status) AS status,
                COUNT(*) AS transaction_count
            FROM transactions
            GROUP BY UPPER(status)
            """
        ).fetchall()

        return {
            "total_transactions": total,
            "total_amount": result["total_amount"] or 0,
            "average_amount": result["average_amount"] or 0,
            "successful_transactions": successful,
            "failed_transactions": failed,
            "success_rate": round(success_rate, 2),
            "failure_rate": round(failure_rate, 2),
            "payment_methods": [dict(row) for row in payment_methods],
            "statuses": [dict(row) for row in statuses],
        }

    finally:
        connection.close()
@app.get("/api/suspicious-transactions")
def get_suspicious_transactions():
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM transactions
            ORDER BY transaction_timestamp DESC
            """
        ).fetchall()

        suspicious_transactions = []

        for row in rows:
            transaction = dict(row)
            reasons = detect_fraud(transaction)

            if reasons:
                transaction["fraud_reasons"] = reasons
                transaction["risk_level"] = (
                    "HIGH"
                    if transaction["transaction_amount"] >= 50000
                    else "MEDIUM"
                )

                suspicious_transactions.append(transaction)

        return suspicious_transactions

    finally:
        connection.close()