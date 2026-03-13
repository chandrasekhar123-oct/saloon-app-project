from extensions import db

class SalonGallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salon.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    salon = db.relationship('Salon', backref=db.backref('gallery', lazy=True))

    def __repr__(self):
        return f'<SalonGallery {self.id} for {self.salon_id}>'
