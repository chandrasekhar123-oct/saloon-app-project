import sqlite3
import os

db_path = r'e:\projects\Saloon_webapp\saloonbackend\instance\saloon.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create complaint table
    try:
        print("Creating complaint table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaint (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL,
                target_type VARCHAR(20) NOT NULL,
                target_id INTEGER NOT NULL,
                subject VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reporter_id) REFERENCES user (id)
            )
        ''')
    except sqlite3.OperationalError as e:
        print(f"Complaint Table: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
