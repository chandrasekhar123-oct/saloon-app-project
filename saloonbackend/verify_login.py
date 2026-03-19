from app import app
from models import User
from werkzeug.security import check_password_hash

with app.app_context():
    user = User.query.filter_by(phone='9000012345').first()
    if user:
        match = check_password_hash(user.password, 'user123')
        print(f"User found: {user.name}")
        print(f"Password 'user123' match: {match}")
        print(f"Hash in DB: {user.password}")
    else:
        print("User not found.")
