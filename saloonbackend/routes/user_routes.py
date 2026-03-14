from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Salon, Service, Booking
from datetime import datetime
import random
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
except ImportError:
    id_token = None # Will handle this in the route

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    password = data.get('password')

    if User.query.filter_by(phone=phone).first():
        return jsonify({"message": "User already exists", "status": "error"}), 400

    pwd = generate_password_hash(password)
    user = User(name=name, phone=phone, password=pwd)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "status": "success", "user_id": user.id})

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')

    user = User.query.filter_by(phone=phone).first()
    if user and check_password_hash(user.password, password):
        return jsonify({"message": "Login successful", "status": "success", "user_id": user.id})
    return jsonify({"message": "Invalid credentials", "status": "error"}), 401
    
@user_bp.route('/google-login', methods=['POST'])
def google_login():
    if id_token is None:
        return jsonify({"message": "google-auth library not installed on server", "status": "error"}), 500
        
    data = request.json
    token = data.get('credential')
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
        
        google_id = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name')
        picture = idinfo.get('picture')
        
        # 1. Try to find user by google_id
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # 2. Try to find user by email
            user = User.query.filter_by(email=email).first()
            if user:
                # Link google account to existing email
                user.google_id = google_id
                if not user.profile_image:
                    user.profile_image = picture
            else:
                # 3. Create new user
                user = User(name=name, email=email, google_id=google_id, profile_image=picture)
                db.session.add(user)
            db.session.commit()
            
        # Log the user in
        session['portal_user_id'] = user.id
        
        return jsonify({
            "message": "Login successful", 
            "status": "success", 
            "user_id": user.id,
            "user": {
                "name": user.name,
                "email": user.email,
                "profile_image": user.profile_image
            }
        })
        
    except ValueError as e:
        return jsonify({"message": f"Invalid token: {str(e)}", "status": "error"}), 400
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

@user_bp.route('/salons', methods=['GET'])
def get_salons():
    location = request.args.get('location')
    category = request.args.get('category')
    
    query = Salon.query.filter_by(is_active=True)
    
    if location:
        # Simple case-insensitive search for location
        query = query.filter(Salon.location.ilike(f"%{location}%"))
    if category:
        query = query.filter(Salon.category.contains(category))
        
    salons = query.all()
    result = []
    for s in salons:
        result.append({
            "id": s.id,
            "name": s.name,
            "category": s.category or "Barber Shop",
            "address": s.address,
            "location": s.location,
            "map_url": s.map_url,
            "image_url": s.image_url,
            "rating": s.rating,
            "is_open": s.is_open
        })
    return jsonify(result)

@user_bp.route('/salon/<int:id>', methods=['GET'])
def get_salon_details(id):
    s = Salon.query.get_or_404(id)
    return jsonify({
        "id": s.id,
        "name": s.name,
        "address": s.address,
        "location": s.location,
        "map_url": s.map_url,
        "image_url": s.image_url,
        "rating": s.rating,
        "upi_id": s.upi_id,
        "qr_code_url": s.qr_code_url,
        "opening_time": s.opening_time,
        "closing_time": s.closing_time
    })

@user_bp.route('/salon/<int:id>/services', methods=['GET'])
def get_services(id):
    services = Service.query.filter_by(salon_id=id).all()
    result = []
    for s in services:
        result.append({
            "id": s.id,
            "name": s.name,
            "price": s.price,
            "duration": s.duration,
            "description": s.description,
            "image_url": s.image_url
        })
    return jsonify(result)

@user_bp.route('/salon/<int:id>/workers', methods=['GET'])
def get_salon_workers(id):
    from models import Worker
    workers = Worker.query.filter_by(salon_id=id, is_approved=True).all()
    result = []
    for w in workers:
        result.append({
            "id": w.id,
            "name": w.name,
            "skill": w.skill or "Expert",
            "experience": w.experience,
            "image_url": w.image_url or f"https://ui-avatars.com/api/?name={w.name}&background=dc2743&color=fff&size=100",
            "status": w.status
        })
    return jsonify(result)


@user_bp.route('/booking/create', methods=['POST'])
def create_booking():
    data = request.json
    user_id = data.get('user_id')
    worker_id = data.get('worker_id')
    salon_id = data.get('salon_id')
    service_id = data.get('service_id')
    slot_time_str = data.get('slot_time') # Expected: 'YYYY-MM-DD HH:MM:SS'
    
    # Generate random 4-6 digit OTP
    otp = str(random.randint(1000, 9999))
    
    booking = Booking(
        user_id=user_id,
        worker_id=worker_id,
        salon_id=salon_id,
        service_id=service_id,
        slot_time=datetime.strptime(slot_time_str, '%Y-%m-%d %H:%M:%S'),
        status='pending',
        otp=otp
    )
    db.session.add(booking)
    db.session.commit()
    
    # 📱 Send SMS Awareness
    from utils.sms_service import SMSService
    user_phone = data.get('phone') or User.query.get(user_id).phone
    SMSService.send_booking_confirmation(user_phone, booking.salon.name, slot_time_str)

    return jsonify({"message": "Booking created", "status": "success", "booking_id": booking.id, "otp": otp})

@user_bp.route('/booking/<int:user_id>', methods=['GET'])
@user_bp.route('/api/bookings/<int:user_id>', methods=['GET'])
def get_bookings(user_id):
    from datetime import datetime
    bookings = Booking.query.filter_by(user_id=user_id).all()
    result = []
    now = datetime.now().date()
    for b in bookings:
        days_left = (b.slot_time.date() - now).days
        message = ""
        if b.status == 'accepted':
            if days_left > 0:
                message = f"Booking is in {days_left} days. Your OTP is saved here."
            elif days_left == 0:
                message = "Your service is today! Present this OTP at the shop."
            else:
                message = "This booking date has passed."

        result.append({
            "id": b.id,
            "service": b.service.name if b.service else "Deleted Service",
            "salon": b.salon.name if b.salon else "Deleted Salon",
            "status": b.status,
            "slot_time": b.slot_time.strftime('%Y-%m-%d %H:%M:%S'),
            "otp": b.otp,
            "map_url": b.salon.map_url if b.salon else "#",
            "days_left": days_left,
            "message": message
        })
    return jsonify(result)
@user_bp.route('/complaint', methods=['POST'])
def raise_complaint():
    from models import Complaint
    data = request.json
    user_id = data.get('user_id')
    target_type = data.get('target_type') # 'worker' or 'owner'
    target_id = data.get('target_id')
    subject = data.get('subject')
    description = data.get('description')
    
    if not all([user_id, target_type, target_id, subject, description]):
        return jsonify({"message": "All fields are required", "status": "error"}), 400
        
    complaint = Complaint(
        reporter_id=user_id,
        target_type=target_type,
        target_id=target_id,
        subject=subject,
        description=description
    )
    db.session.add(complaint)
    db.session.commit()
    return jsonify({"message": "Complaint filed successfully. Admin will review it.", "status": "success"})
