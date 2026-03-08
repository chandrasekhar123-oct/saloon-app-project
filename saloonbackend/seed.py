from app import app
from models import db, Owner, Salon, Service, Worker, User
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        print("Cleaning database...")
        db.drop_all()
        db.create_all()

        # 1. Create Owners
        pwd = generate_password_hash('admin123')
        owner1 = Owner(name="Chandra Sekhar", email="chandra@saloonessy.com", phone="8500741873", password=pwd)
        owner2 = Owner(name="Anjali Sharma", email="anjali@saloonessy.com", phone="9988776655", password=pwd)
        db.session.add_all([owner1, owner2])
        db.session.commit()

        # 2. Create Salons (Hyderabad focused for demo)
        s1 = Salon(
            owner_id=owner1.id, name="Royal Grooming Lounge", 
            address="HITEC City, Madhapur", location="Hyderabad", 
            rating=4.9, image_url="https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?w=800&q=80"
        )
        s2 = Salon(
            owner_id=owner1.id, name="Urban Blade Studio", 
            address="Jubilee Hills Road No. 36", location="Hyderabad", 
            rating=4.7, image_url="https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800&q=80"
        )
        s3 = Salon(
            owner_id=owner2.id, name="The Glow Spa & Salon", 
            address="Gachibowli DLF Road", location="Hyderabad", 
            rating=4.8, image_url="https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80"
        )
        s4 = Salon(
            owner_id=owner2.id, name="Classic Cuts", 
            address="Kukatpally Housing Board", location="Hyderabad", 
            rating=4.5, image_url="https://images.unsplash.com/photo-1599351431247-f57933847020?w=800&q=80"
        )
        db.session.add_all([s1, s2, s3, s4])
        db.session.commit()

        # 3. Create Services
        services_data = [
            (s1, "Executive Haircut", 450, 40, "Precision cut with hair wash and styling."),
            (s1, "Luxury Beard Grooming", 300, 30, "Steam, oil treatment, and sharp lining."),
            (s1, "Head Massage (15 min)", 200, 15, "Relaxing traditional head massage."),
            (s2, "Skin Fade Special", 350, 45, "Ultra-sharp modern fade."),
            (s2, "Global Hair Color", 1200, 90, "Premium ammonia-free coloring."),
            (s3, "Full Body Spa", 2500, 120, "Swedish massage with essential oils."),
            (s3, "Hydrafacial", 3500, 60, "Deep cleansing and skin rejuvenation."),
            (s4, "Basic Haircut", 150, 20, "Quick and clean trim."),
            (s4, "Hot Towel Shave", 100, 15, "Traditional straight razor shave."),
        ]

        for salon, name, price, dur, desc in services_data:
            db.session.add(Service(salon_id=salon.id, name=name, price=price, duration=dur, description=desc))

        # 4. Create Workers
        worker_pwd = generate_password_hash('worker123')
        w1 = Worker(salon_id=s1.id, name="Raj Kumar", phone="7766554433", password=worker_pwd, skill="Expert Stylist", experience=8, status="online", image_url="https://i.pravatar.cc/300?img=11")
        w2 = Worker(salon_id=s1.id, name="Amit Singh", phone="8877665544", password=worker_pwd, skill="Beard Specialist", experience=5, status="online", image_url="https://i.pravatar.cc/300?img=12")
        w3 = Worker(salon_id=s3.id, name="Priya Das", phone="9988776611", password=worker_pwd, skill="Spa Therapist", experience=6, status="online", image_url="https://i.pravatar.cc/300?img=32")
        db.session.add_all([w1, w2, w3])

        # 5. Create Sample User
        user_pwd = generate_password_hash('user123')
        user = User(name="Test User", phone="9000012345", password=user_pwd)
        db.session.add(user)

        db.session.commit()
        print("Database seeded with high-quality data!")

if __name__ == "__main__":
    seed_data()
