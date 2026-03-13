from extensions import db

class Salon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Text, default="Barber Shop") # Supports multiple categories comma-separated
    address = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(100)) # Added state field
    location = db.Column(db.String(100)) # City/Area
    image_url = db.Column(db.String(500), default="https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    opening_time = db.Column(db.String(10), default="09:00 AM")
    closing_time = db.Column(db.String(10), default="09:00 PM")
    map_url = db.Column(db.Text)
    rating = db.Column(db.Float, default=4.5)
    upi_id = db.Column(db.String(100)) # e.g., owner@upi
    qr_code_url = db.Column(db.String(255)) # Image link for QR code
    logo_url = db.Column(db.String(500))
    shop_photos = db.Column(db.Text) # Stored as comma-separated URLs or JSON string
    excellence_categories = db.Column(db.Text) # Comma-separated categories like "Top Rated, Hygiene Champion"
    is_active = db.Column(db.Boolean, default=True)

    @property
    def is_open(self):
        from datetime import datetime
        try:
            now = datetime.now().time()
            o_str = self.opening_time.strip().upper() if self.opening_time else "09:00 AM"
            c_str = self.closing_time.strip().upper() if self.closing_time else "09:00 PM"
            
            def parse_time(t_str):
                for fmt in ("%I:%M %p", "%H:%M", "%I:%M%p", "%H:%M:%S"):
                    try:
                        return datetime.strptime(t_str, fmt).time()
                    except ValueError:
                        continue
                raise ValueError(f"Unknown format: {t_str}")

            open_time = parse_time(o_str)
            close_time = parse_time(c_str)

            if open_time < close_time:
                return open_time <= now <= close_time
            else: # Overnight case
                return now >= open_time or now <= close_time
        except Exception as e:
            # Log the error if possible, but don't crash the page
            print(f"Time parsing error for salon {self.id}: {e}")
            return True # Show if error parsing
    
    services = db.relationship('Service', backref='salon', lazy=True)
    workers = db.relationship('Worker', backref='salon', lazy=True)
    bookings = db.relationship('Booking', backref='salon', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salon.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer) # in minutes
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
