from flask_login import UserMixin
from extensions import db
from .base_user import BaseUserMixin

class Owner(UserMixin, BaseUserMixin, db.Model):
    __tablename__ = 'owner'
    id = db.Column(db.Integer, primary_key=True)
    shop = db.relationship('Salon', backref='owner', uselist=False, lazy=True)

    def get_id(self):
        return f"owner:{self.id}"

class User(UserMixin, BaseUserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def get_id(self):
        return f"user:{self.id}"

class Worker(UserMixin, BaseUserMixin, db.Model):
    __tablename__ = 'worker'
    id = db.Column(db.Integer, primary_key=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salon.id'), nullable=True) # Optional link
    skill = db.Column(db.String(200)) # e.g., "Haircut, Styling"
    experience = db.Column(db.Integer)
    image_url = db.Column(db.String(500), default="https://i.pravatar.cc/300")
    state = db.Column(db.String(100), nullable=True) # Added state
    city = db.Column(db.String(100), nullable=True)  # Added city
    status = db.Column(db.String(20), default='offline') # online/offline
    is_approved = db.Column(db.Boolean, default=True) # Changed for automatic approval
    upi_id = db.Column(db.String(100), nullable=True)
    instagram_url = db.Column(db.String(200), nullable=True)
    facebook_url = db.Column(db.String(200), nullable=True)
    
    # Financial/Payment Fields
    payment_type = db.Column(db.String(20), default='commission') # 'commission' or 'salary'
    salary_amount = db.Column(db.Float, default=0.0) # Fixed salary if payment_type is 'salary'
    commission_rate = db.Column(db.Float, default=50.0) # Percentage worker gets per service (if commission)
    
    is_owner = db.Column(db.Boolean, default=False) # True if this worker record is the owner themselves
    
    total_earnings = db.Column(db.Float, default=0.0)   # Total lifetime earnings for the worker
    current_balance = db.Column(db.Float, default=0.0)  # Amount currently owed to the worker (unpaid)
    bookings = db.relationship('Booking', backref='worker', lazy=True)

    @property
    def rating(self):
        # Calculate average rating using a direct SQL aggregate query to avoid N+1 issues
        from sqlalchemy.sql import func
        from models import Review, Booking
        
        avg_rating = db.session.query(func.avg(Review.rating)).join(Booking).filter(
            Booking.worker_id == self.id,
            Booking.status == 'completed'
        ).scalar()
        
        if avg_rating is None:
            return 4.5 # Default rating for new workers
            
        return round(float(avg_rating), 1)

    def get_id(self):
        return f"worker:{self.id}"

class SuperAdmin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def get_id(self):
        return f"admin:{self.id}"
