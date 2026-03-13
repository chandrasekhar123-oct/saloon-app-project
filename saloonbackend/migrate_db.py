import sqlite3
import os

db_path = r'd:\saloon app project\saloonbackend\instance\saloon.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Adding upi_id column...")
        cursor.execute("ALTER TABLE worker ADD COLUMN upi_id VARCHAR(100)")
    except sqlite3.OperationalError as e:
        print(f"upi_id: {e}")

    try:
        print("Adding instagram_url column...")
        cursor.execute("ALTER TABLE worker ADD COLUMN instagram_url VARCHAR(200)")
    except sqlite3.OperationalError as e:
        print(f"instagram_url: {e}")

    try:
        print("Adding facebook_url column...")
        cursor.execute("ALTER TABLE worker ADD COLUMN facebook_url VARCHAR(200)")
    except sqlite3.OperationalError as e:
        print(f"facebook_url: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
