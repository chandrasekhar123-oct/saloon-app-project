from extensions import db

class BaseUserMixin:
    """
    A mixin that provides the core fields required for any user type in the system.
    This helps enforce the DRY principle across Owner, User, and Worker models.
    """
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    # Secure password reset token (replaces the insecure ID-based reset URL)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    # Most user types use profile_image. Worker overrides this behavior using image_url currently.
    profile_image = db.Column(db.String(500), nullable=True)
