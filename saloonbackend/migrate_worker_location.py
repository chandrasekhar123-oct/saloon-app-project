import sqlite3
import os

db_path = r'c:\Users\LENOVO\OneDrive\Desktop\saloonbackend\instance\saloon.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking for location columns in worker table...")
    
    # Check if columns exist in worker
    cursor.execute("PRAGMA table_info(worker)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'state' not in columns:
        print("Adding 'state' column to worker table...")
        cursor.execute("ALTER TABLE worker ADD COLUMN state VARCHAR(100)")
    else:
        print("'state' column already exists in worker table.")

    if 'city' not in columns:
        print("Adding 'city' column to worker table...")
        cursor.execute("ALTER TABLE worker ADD COLUMN city VARCHAR(100)")
    else:
        print("'city' column already exists in worker table.")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
