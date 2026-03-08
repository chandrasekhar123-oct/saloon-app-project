from extensions import db
from datetime import datetime

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salon.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    discount_tag = db.Column(db.String(50), nullable=False) # e.g. "50% OFF"
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    salon = db.relationship('Salon', backref=db.backref('offers', lazy=True))

    def __repr__(self):
        return f'<Offer {self.title}>'
