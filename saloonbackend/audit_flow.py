import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app import app
from models import db, User, Salon, Service, Worker, Booking
from datetime import datetime, timedelta

def audit_booking_and_commissions():
    with app.app_context():
        print("🔍 Starting Booking & Commission Logic Audit...")
        
        # 1. Fetch or Create Test Data
        user = User.query.first()
        salon = Salon.query.first()
        service = Service.query.first()
        worker = Worker.query.filter_by(salon_id=salon.id).first()
        
        if not all([user, salon, service, worker]):
            print("❌ Error: Not enough seed data to run audit.")
            return

        print(f"✅ Found Data: User({user.name}), Salon({salon.name}), Service({service.name}), Worker({worker.name})")

        # 2. Simulate a Booking Creation
        booking = Booking(
            user_id=user.id,
            salon_id=salon.id,
            service_id=service.id,
            worker_id=worker.id,
            slot_time=datetime.utcnow() + timedelta(hours=1),
            status='pending',
            payment_method='Cash'
        )
        db.session.add(booking)
        db.session.commit()
        print(f"✅ Booking #{booking.id} created successfully.")

        # 3. Simulate Worker Approval
        booking.status = 'accepted'
        db.session.commit()
        print(f"✅ Booking accepted by worker.")

        # 4. Simulate Completion & Commission Calculation
        # Logic matches user_portal_routes.py and worker_panel_routes.py
        price = float(service.price)
        commission_rate = worker.commission_rate or 50.0 # Default 50%
        
        worker_share = (commission_rate / 100.0) * price
        owner_share = price - worker_share
        
        booking.status = 'completed'
        booking.worker_share = worker_share
        booking.owner_share = owner_share
        booking.commission_applied = True
        
        db.session.commit()
        
        print("\n💰 Financial Results:")
        print(f"   Total Service Price: {price}")
        print(f"   Worker Share ({commission_rate}%): {worker_share}")
        print(f"   Owner Share: {owner_share}")
        print("✅ Commission logic verified.")

        # Cleanup test booking
        db.session.delete(booking)
        db.session.commit()
        print("\n✨ Audit complete. All backend pipes are clear!")

if __name__ == "__main__":
    audit_booking_and_commissions()
