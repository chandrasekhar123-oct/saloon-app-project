import sqlite3
import os

db_path = r'e:\projects\Saloon_webapp\saloonbackend\instance\saloon.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add is_active to User
    try:
        print("Adding is_active column to User table...")
        cursor.execute("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1")
    except sqlite3.OperationalError as e:
        print(f"User is_active: {e}")

    # Add is_active to Owner
    try:
        print("Adding is_active column to Owner table...")
        cursor.execute("ALTER TABLE owner ADD COLUMN is_active BOOLEAN DEFAULT 1")
    except sqlite3.OperationalError as e:
        print(f"Owner is_active: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
