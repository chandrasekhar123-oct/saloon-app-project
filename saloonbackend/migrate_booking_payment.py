from app import app
from extensions import db
from sqlalchemy import text

def migrate():
    with app.app_context():
        # Check if columns exist and add them if not
        try:
            db.session.execute(text('ALTER TABLE booking ADD COLUMN payment_method VARCHAR(20)'))
            print("Added payment_method column to booking table.")
        except Exception as e:
            print(f"payment_method column might already exist or error: {e}")

        try:
            db.session.execute(text("ALTER TABLE booking ADD COLUMN payment_status VARCHAR(20) DEFAULT 'Pending'"))
            print("Added payment_status column to booking table.")
        except Exception as e:
            print(f"payment_status column might already exist or error: {e}")
        
        db.session.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
