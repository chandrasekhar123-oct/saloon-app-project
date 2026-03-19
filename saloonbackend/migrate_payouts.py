import sqlite3
import os

db_path = r'e:\projects\Saloon_webapp\saloonbackend\instance\saloon.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns_to_add = [
        ("payment_type", "VARCHAR(20) DEFAULT 'commission'"),
        ("salary_amount", "FLOAT DEFAULT 0.0"),
        ("commission_rate", "FLOAT DEFAULT 50.0"),
        ("is_owner", "BOOLEAN DEFAULT 0"),
        ("total_earnings", "FLOAT DEFAULT 0.0"),
        ("current_balance", "FLOAT DEFAULT 0.0")
    ]

    for col_name, col_type in columns_to_add:
        try:
            print(f"Adding {col_name} column...")
            cursor.execute(f"ALTER TABLE worker ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError as e:
            print(f"Skipping {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Payout fields migration finished.")

if __name__ == "__main__":
    migrate()
