import sqlite3
import os

def migrate():
    # Path to your database
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'saloon.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Starting migration for Owner and Worker tables...")

    try:
        # Update Owner table
        print("Migrating Owner table...")
        cursor.execute("ALTER TABLE owner ADD COLUMN google_id VARCHAR(100)")
    except sqlite3.OperationalError as e:
        print(f"Owner google_id column fallback: {e}")

    try:
        # Update Worker table
        print("Migrating Worker table...")
        cursor.execute("ALTER TABLE worker ADD COLUMN email VARCHAR(120)")
    except sqlite3.OperationalError as e:
        print(f"Worker email column fallback: {e}")

    try:
        cursor.execute("ALTER TABLE worker ADD COLUMN google_id VARCHAR(100)")
    except sqlite3.OperationalError as e:
        print(f"Worker google_id column fallback: {e}")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
