from app import app
from models import db, User, Worker, Owner

with app.app_context():
    users = User.query.all()
    print(f"Total Users: {len(users)}")
    for u in users:
        print(f"User: {u.name}, Phone: {u.phone}, Email: {u.email}")
    
    workers = Worker.query.all()
    print(f"Total Workers: {len(workers)}")
    for w in workers:
        print(f"Worker: {w.name}, Phone: {w.phone}")
