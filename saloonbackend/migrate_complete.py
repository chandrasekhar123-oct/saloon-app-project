import sqlite3
import os

db_path = r'e:\projects\Saloon_webapp\saloonbackend\instance\saloon.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Worker table columns
    worker_cols = [
        ("payment_type", "VARCHAR(20) DEFAULT 'commission'"),
        ("salary_amount", "FLOAT DEFAULT 0.0"),
        ("commission_rate", "FLOAT DEFAULT 50.0"),
        ("is_owner", "BOOLEAN DEFAULT 0"),
        ("total_earnings", "FLOAT DEFAULT 0.0"),
        ("current_balance", "FLOAT DEFAULT 0.0")
    ]

    # Booking table columns
    booking_cols = [
        ("worker_share", "FLOAT DEFAULT 0.0"),
        ("owner_share", "FLOAT DEFAULT 0.0"),
        ("commission_applied", "BOOLEAN DEFAULT 0")
    ]

    for col_name, col_type in worker_cols:
        try:
            cursor.execute(f"ALTER TABLE worker ADD COLUMN {col_name} {col_type}")
            print(f"Added {col_name} to worker.")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists in worker.")

    for col_name, col_type in booking_cols:
        try:
            cursor.execute(f"ALTER TABLE booking ADD COLUMN {col_name} {col_type}")
            print(f"Added {col_name} to booking.")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists in booking.")

    conn.commit()
    conn.close()
    print("Migration check finished.")

if __name__ == "__main__":
    migrate()
