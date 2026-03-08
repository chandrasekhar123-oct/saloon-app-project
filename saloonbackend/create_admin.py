from app import app
from extensions import db
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        from models import SuperAdmin
        # Check if admin already exists
        if SuperAdmin.query.filter_by(username='admin').first():
            print("Admin already exists.")
            return

        admin = SuperAdmin(
            name='System Administrator',
            username='admin',
            password=generate_password_hash('superadmin123')
        )
        db.session.add(admin)
        db.session.commit()
        print("Super Admin created: admin / superadmin123")

if __name__ == "__main__":
    create_admin()
