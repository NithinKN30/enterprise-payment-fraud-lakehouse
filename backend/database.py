from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "datasets"
DB_PATH = DATA_DIR / "transactions.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                merchant_id TEXT NOT NULL,
                transaction_timestamp TEXT NOT NULL,
                transaction_amount REAL NOT NULL,
                currency TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                country TEXT NOT NULL,
                device_id TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )

        connection.commit()
    finally:
        connection.close()