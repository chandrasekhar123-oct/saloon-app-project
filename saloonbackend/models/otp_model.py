from extensions import db
from datetime import datetime, timedelta
import random

class OTPVerification(db.Model):
    __tablename__ = 'otp_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), index=True, nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), default='login') # login, register, reset
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(OTPVerification, self).__init__(**kwargs)
        if not self.otp:
            self.otp = str(random.randint(100000, 999999))
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(minutes=10)

    @classmethod
    def verify_otp(cls, phone, otp, purpose='login'):
        """
        Verifies if an OTP exists and is valid for the given phone and purpose.
        """
        record = cls.query.filter_by(
            phone=phone, 
            otp=otp, 
            purpose=purpose,
            is_verified=False
        ).filter(cls.expires_at > datetime.utcnow()).order_by(cls.id.desc()).first()
        
        if record:
            record.is_verified = True
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f'<OTP {self.otp} for {self.phone}>'
