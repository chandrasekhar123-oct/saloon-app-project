from extensions import db
from datetime import datetime

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False) # 'worker' or 'owner'
    target_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, warned, blocked, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reporter = db.relationship('User', backref=db.backref('complaints_filed', lazy=True))

    def __repr__(self):
        return f'<Complaint {self.id} against {self.target_type}:{self.target_id}>'
