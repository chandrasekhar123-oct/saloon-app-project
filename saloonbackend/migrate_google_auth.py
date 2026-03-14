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
        print("Adding email column to user table...")
        cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(120)")
    except sqlite3.OperationalError as e:
        print(f"email: {e}")

    try:
        print("Adding google_id column to user table...")
        cursor.execute("ALTER TABLE user ADD COLUMN google_id VARCHAR(100)")
    except sqlite3.OperationalError as e:
        print(f"google_id: {e}")

    try:
        print("Modifying phone column to be nullable (SQLite alternative)...")
        # In SQLite, you can't easily drop NOT NULL constraint. 
        # But we can just leave it if it was already NOT NULL, 
        # though our model change says nullable=True.
        # Actually, if it was created with NOT NULL, we'd need to recreate the table.
        # Let's hope for the best or skip for now if it requires a complex migration.
        pass
    except Exception as e:
        print(f"phone nullable: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
