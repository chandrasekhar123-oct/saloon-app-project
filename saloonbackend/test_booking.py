from app import app
from models import db, User, Salon, Service, Worker, Booking, Notification
from datetime import datetime, timedelta

with app.app_context():
    user = User.query.filter_by(phone='+919000012345').first()
    salon = Salon.query.first()
    service = Service.query.filter_by(salon_id=salon.id).first()
    worker = Worker.query.filter_by(salon_id=salon.id).first()
    
    if user and salon and service and worker:
        slot = datetime.now() + timedelta(days=1)
        booking = Booking(
            user_id=user.id,
            salon_id=salon.id,
            service_id=service.id,
            worker_id=worker.id,
            slot_time=slot,
            status='pending'
        )
        db.session.add(booking)
        
        notif = Notification(
            user_id=user.id,
            title="Test Booking",
            message=f"Booking for {service.name}",
            type="booking"
        )
        db.session.add(notif)
        db.session.commit()
        print(f"Booking created for {user.name} at {salon.name} for {service.name}")
    else:
        print("Required entities not found for booking test.")
