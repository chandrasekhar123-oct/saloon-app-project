
import sqlite3
import os

db_path = r'd:\saloon app project\saloonbackend\instance\saloon.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Columns to add to 'booking' table
    booking_columns = [
        ('worker_share', 'REAL DEFAULT 0.0'),
        ('owner_share', 'REAL DEFAULT 0.0'),
        ('commission_applied', 'BOOLEAN DEFAULT 0')
    ]

    # Columns to add to 'worker' table
    worker_columns = [
        ('commission_rate', 'REAL DEFAULT 50.0'),
        ('total_earnings', 'REAL DEFAULT 0.0'),
        ('current_balance', 'REAL DEFAULT 0.0')
    ]

    def add_columns(table_name, columns):
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = [row[1] for row in cursor.fetchall()]
        
        for col_name, col_type in columns:
            if col_name not in existing_cols:
                print(f"Adding column {col_name} to table {table_name}...")
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"Error adding {col_name}: {e}")
            else:
                print(f"Column {col_name} already exists in {table_name}.")

    add_columns('booking', booking_columns)
    add_columns('worker', worker_columns)

    conn.commit()
    conn.close()
    print("Migration completed!")

if __name__ == "__main__":
    migrate()
