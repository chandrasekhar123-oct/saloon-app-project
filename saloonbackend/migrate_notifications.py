import sqlite3
import os

db_path = r'e:\projects\Saloon_webapp\saloonbackend\instance\saloon.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Adding worker_notified column to booking...")
        cursor.execute("ALTER TABLE booking ADD COLUMN worker_notified BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError as e:
        print(f"worker_notified: {e}")

    try:
        print("Adding user_notified column to booking...")
        cursor.execute("ALTER TABLE booking ADD COLUMN user_notified BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError as e:
        print(f"user_notified: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
