from extensions import db
from datetime import datetime

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=True)  # nullable: worker may be deleted
    salon_id = db.Column(db.Integer, db.ForeignKey('salon.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    slot_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending/accepted/rejected/completed
    otp = db.Column(db.String(6))
    payment_method = db.Column(db.String(20)) # Cash/Online
    payment_status = db.Column(db.String(20), default='Pending') # Pending/Paid
    worker_message = db.Column(db.String(100)) # Quick message like 'I am on my way'
    worker_share = db.Column(db.Float, default=0.0)
    owner_share = db.Column(db.Float, default=0.0)
    commission_applied = db.Column(db.Boolean, default=False)
    worker_notified = db.Column(db.Boolean, default=False)
    user_notified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship for convenience
    service = db.relationship('Service')
