from app import app
from extensions import db
from models.user_model import SuperAdmin
from werkzeug.security import generate_password_hash
import sys

def create_admin(name, username, password):
    with app.app_context():
        # Check if admin already exists
        existing = SuperAdmin.query.filter_by(username=username).first()
        if existing:
            print(f"Error: Admin with username '{username}' already exists.")
            return

        new_admin = SuperAdmin(
            name=name,
            username=username,
            password=generate_password_hash(password)
        )
        db.session.add(new_admin)
        db.session.commit()
        print(f"Success: Admin account created for '{name}' with username '{username}'")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_admin.py <Name> <Username> <Password>")
        print("Example: python create_admin.py 'CEO Admin' admin password123")
    else:
        create_admin(sys.argv[1], sys.argv[2], sys.argv[3])
