from flask_login import UserMixin
from extensions import db

class Owner(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_image = db.Column(db.String(500), nullable=True)
    gender = db.Column(db.String(10), nullable=True) # Added gender field
    is_active = db.Column(db.Boolean, default=True) # Added for administrative control
    shop = db.relationship('Salon', backref='owner', uselist=False, lazy=True)

    def get_id(self):
        return f"owner:{self.id}"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_image = db.Column(db.String(500), nullable=True)
    gender = db.Column(db.String(10), nullable=True) # Added gender field
    is_active = db.Column(db.Boolean, default=True) # Added for administrative control
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def get_id(self):
        return f"user:{self.id}"

class Worker(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salon.id'), nullable=True) # Optional link
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    skill = db.Column(db.String(200)) # e.g., "Haircut, Styling"
    experience = db.Column(db.Integer)
    image_url = db.Column(db.String(500), default="https://i.pravatar.cc/300")
    gender = db.Column(db.String(10), nullable=True)
    state = db.Column(db.String(100), nullable=True) # Added state
    city = db.Column(db.String(100), nullable=True)  # Added city
    status = db.Column(db.String(20), default='offline') # online/offline
    is_active = db.Column(db.Boolean, default=True)
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
        # Calculate average rating from reviews linked via bookings
        if not self.bookings:
            return 4.5 # Default rating for new workers
        
        ratings = []
        for b in self.bookings:
            if b.status == 'completed' and hasattr(b, 'review') and b.review:
                ratings.append(b.review.rating)
        
        if not ratings:
            return 4.5
            
        return round(sum(ratings) / len(ratings), 1)

    def get_id(self):
        return f"worker:{self.id}"

class SuperAdmin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def get_id(self):
        return f"admin:{self.id}"
