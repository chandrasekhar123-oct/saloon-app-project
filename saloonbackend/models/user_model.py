from flask_login import UserMixin
from extensions import db

class Owner(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_image = db.Column(db.String(500), nullable=True)
    gender = db.Column(db.String(10), nullable=True) # Added gender field
    shop = db.relationship('Salon', backref='owner', uselist=False, lazy=True)

    def get_id(self):
        return f"owner:{self.id}"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_image = db.Column(db.String(500), nullable=True)
    gender = db.Column(db.String(10), nullable=True) # Added gender field
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def get_id(self):
        return f"user:{self.id}"

class Worker(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salon.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    skill = db.Column(db.String(200)) # e.g., "Haircut, Styling"
    experience = db.Column(db.Integer)
    image_url = db.Column(db.String(500), default="https://i.pravatar.cc/300")
    gender = db.Column(db.String(10), nullable=True)
    state = db.Column(db.String(100), nullable=True) # Added state
    city = db.Column(db.String(100), nullable=True)  # Added city
    status = db.Column(db.String(20), default='offline') # online/offline
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='worker', lazy=True)

    def get_id(self):
        return f"worker:{self.id}"
