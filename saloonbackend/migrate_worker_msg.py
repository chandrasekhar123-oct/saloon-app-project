from app import app
from extensions import db
from sqlalchemy import text

def migrate():
    with app.app_context():
        # Check if columns exist and add them if not
        try:
            db.session.execute(text('ALTER TABLE booking ADD COLUMN worker_message VARCHAR(100)'))
            print("Added worker_message column to booking table.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")
        
        db.session.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
