from app import app
from models import Salon
with app.app_context():
    salons = Salon.query.all()
    for s in salons:
        print(f"ID: {s.id} | Name: {s.name} | Category: [{s.category}]")
