from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Owner(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gst_number = db.Column(db.String(20), nullable=True)
    shop = db.relationship('Shop', backref='owner', uselist=False)

class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    opening_time = db.Column(db.String(10), nullable=False)
    closing_time = db.Column(db.String(10), nullable=False)
    images = db.Column(db.Text)
    map_url = db.Column(db.Text) # For Google Maps Embed URL
    is_closed_temporarily = db.Column(db.Boolean, default=False)
    
    services = db.relationship('Service', backref='shop', lazy=True)
    workers = db.relationship('Worker', backref='shop', lazy=True)
    bookings = db.relationship('Booking', backref='shop', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False) 
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    experience = db.Column(db.Integer)
    photo_url = db.Column(db.String(255))
    skills = db.Column(db.Text)
    assigned_services = db.Column(db.Text)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=True)
    slot_time = db.Column(db.DateTime, nullable=False)
    payment_status = db.Column(db.String(20), default='Pending')
    status = db.Column(db.String(20), default='Pending')
    
    service = db.relationship('Service')
    worker = db.relationship('Worker')

class Earnings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
