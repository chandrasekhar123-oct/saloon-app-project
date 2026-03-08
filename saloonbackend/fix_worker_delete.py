"""
Fix script: Makes booking.worker_id nullable in the existing SQLite database.
Run this ONCE to update the schema without losing any data.
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'saloon.db')

if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Starting DB migration: making booking.worker_id nullable...")

# Step 1: Create a new booking table with worker_id as nullable
cursor.executescript("""
    PRAGMA foreign_keys=OFF;

    CREATE TABLE IF NOT EXISTS booking_new (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES user(id),
        worker_id INTEGER REFERENCES worker(id),   -- NOW NULLABLE
        salon_id INTEGER NOT NULL REFERENCES salon(id),
        service_id INTEGER NOT NULL REFERENCES service(id),
        slot_time DATETIME NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        otp VARCHAR(6),
        payment_method VARCHAR(20),
        payment_status VARCHAR(20) DEFAULT 'Pending',
        worker_message VARCHAR(100),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    INSERT INTO booking_new 
        (id, user_id, worker_id, salon_id, service_id, slot_time, status, otp, payment_method, payment_status, worker_message, created_at)
    SELECT 
        id, user_id, worker_id, salon_id, service_id, slot_time, status, otp, payment_method, payment_status, worker_message, created_at
    FROM booking;

    DROP TABLE booking;
    ALTER TABLE booking_new RENAME TO booking;

    PRAGMA foreign_keys=ON;
""")

conn.commit()
conn.close()
print("✅ Migration successful! booking.worker_id is now nullable.")
print("   You can now delete workers without IntegrityError.")
