from app import app
from models import db, Booking, User

def verify_test():
    with app.app_context():
        bookings = Booking.query.order_by(Booking.id.desc()).limit(3).all()
        print(f"📊 Top {len(bookings)} Latest Bookings:")
        for b in bookings:
            user_name = b.user.name if b.user else "Unknown"
            print(f"   - [ID: {b.id}] User: {user_name}, Time: {b.slot_time}, Worker: {b.worker_id}, Status: {b.status}")

if __name__ == "__main__":
    verify_test()
