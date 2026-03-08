from app import app
from models import Worker, Salon
with app.app_context():
    salon_id = 9
    workers = Worker.query.filter_by(salon_id=salon_id).all()
    print(f"Workers for Salon {salon_id}:")
    for w in workers:
        print(f"ID: {w.id} | Name: {w.name} | Approved: {w.is_approved}")
