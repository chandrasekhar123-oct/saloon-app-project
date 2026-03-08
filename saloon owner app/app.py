from flask import Flask, redirect, url_for
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from datetime import datetime
from models import db, Owner, Shop, Service, Worker, Booking
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'salon-owner-secret-key-456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salon_owner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'owner.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(owner_id):
    return Owner.query.get(int(owner_id))

# ─── BLUEPRINT REGISTRATION ──────────────────────────────────────────

from owner_routes import owner_bp
app.register_blueprint(owner_bp, url_prefix='/owner')

@app.route('/')
def index():
    return redirect(url_for('owner.login'))

def create_seed_data():
    if Owner.query.first(): return
    
    # 1. Create Owner
    pwd = generate_password_hash('admin123')
    o = Owner(name="Chandra Sekhar", email="admin@salonhub.com", phone="9876543210", password=pwd)
    db.session.add(o)
    db.session.flush()
    
    # 2. Create Shop
    s = Shop(owner_id=o.id, name="Royal Grooming Lounge", address="Phase 2, HITEC City, Hyderabad", 
             opening_time="09:00", closing_time="21:00",
             map_url="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3806.216346261234!2d78.3752878!3d17.4482998!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bcb93dc8c5bb6df%3A0x192eef8e9a263c96!2sHITEC%20City%2C%20Hyderabad%2C%20Telangana!5e0!3m2!1sen!2sin!4v1700000000000!5m2!1sen!2sin")
    db.session.add(s)
    db.session.flush()
    
    # 3. Create Services
    s1 = Service(shop_id=s.id, name="Classic Haircut", price=250.0, duration=30, description="Standard precision haircut.")
    s2 = Service(shop_id=s.id, name="Luxury Shave", price=150.0, duration=20, description="Hot towel and straight razor shave.")
    db.session.add_all([s1, s2])
    db.session.flush()
    
    # 4. Create Workers
    w1 = Worker(shop_id=s.id, name="Raj Kumar", experience=5, skills="Haircut, Styling", phone="9988776655")
    db.session.add(w1)
    db.session.flush()
    
    # 5. Create Booking
    b1 = Booking(shop_id=s.id, customer_name="Rahul V", service_id=s1.id, worker_id=w1.id, 
                 slot_time=datetime.now(), status="Pending")
    db.session.add(b1)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_seed_data()
    app.run(debug=True)
