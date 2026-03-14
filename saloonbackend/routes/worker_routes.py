from flask import Blueprint, request, jsonify, current_app
from models import db, Worker, Booking, Salon
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

worker_bp = Blueprint('worker', __name__)

@worker_bp.route('/register', methods=['POST'])
def register():
    # Handle both JSON (app) and Form (web/app with file)
    if request.is_json:
        data = request.json
    else:
        data = request.form

    name = data.get('name')
    phone = data.get('phone')
    password = data.get('password')
    salon_id = data.get('salon_id')
    experience = data.get('experience')
    skill = data.get('skill')

    if Worker.query.filter_by(phone=phone).first():
        return jsonify({"message": "Worker already exists", "status": "error"}), 400

    pwd = generate_password_hash(password)
    worker = Worker(
        name=name, 
        phone=phone, 
        password=pwd, 
        salon_id=salon_id,
        experience=experience,
        skill=skill,
        is_approved=False  # Must be approved by salon owner
    )
    
    # Handle photo upload during registration
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename != '':
            filename = secure_filename(f"worker_reg_{phone}_{int(datetime.now().timestamp())}_{file.filename}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            worker.image_url = request.host_url.rstrip('/') + url_for('static', filename=f"uploads/{filename}")

    db.session.add(worker)
    db.session.commit()
    return jsonify({"message": "Registration successful. Please wait for shop owner approval.", "status": "success"})

@worker_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')

    worker = Worker.query.filter_by(phone=phone).first()
    if worker and check_password_hash(worker.password, password):
        if not worker.is_approved:
            return jsonify({"message": "Your account is pending approval by the shop owner.", "status": "pending"}), 403
        return jsonify({"message": "Worker login successful", "status": "success", "worker_id": worker.id})
    return jsonify({"message": "Invalid credentials", "status": "error"}), 401

@worker_bp.route('/salons', methods=['GET'])
def get_salons():
    salons = Salon.query.all()
    result = []
    for s in salons:
        result.append({
            "id": s.id,
            "name": s.name,
            "location": s.location
        })
    return jsonify(result)

@worker_bp.route('/bookings/<int:id>', methods=['GET'])
def get_bookings(id):
    bookings = Booking.query.filter_by(worker_id=id).all()
    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "user": b.user.name,
            "service": b.service.name,
            "status": b.status,
            "slot_time": b.slot_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result)

@worker_bp.route('/booking/<int:id>/accept', methods=['POST'])
def accept_booking(id):
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({"message": "Booking not found", "status": "error"}), 404
    
    import random, string
    otp = ''.join(random.choices(string.digits, k=4))
    
    booking.status = 'accepted'
    booking.otp = otp
    db.session.commit()
    
    return jsonify({
        "message": "Booking accepted",
        "status": "success",
        "otp": otp
    })

@worker_bp.route('/booking/<int:id>/reject', methods=['POST'])
def reject_booking(id):
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({"message": "Booking not found", "status": "error"}), 404
    booking.status = 'rejected'
    db.session.commit()
    return jsonify({"message": "Booking rejected", "status": "success"})

@worker_bp.route('/booking/<int:id>/verify-otp', methods=['POST'])
def verify_otp(id):
    data = request.json
    otp = data.get('otp')
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({"message": "Booking not found", "status": "error"}), 404
    if booking.otp == otp:
        booking.status = 'completed'
        db.session.commit()
        return jsonify({"message": "OTP verified successfully", "status": "success"})
    return jsonify({"message": "Invalid OTP", "status": "error"}), 400

@worker_bp.route('/<int:id>', methods=['GET'])
def get_worker(id):
    worker = Worker.query.get(id)
    if not worker:
        return jsonify({"message": "Worker not found", "status": "error"}), 404
        
    salon = Salon.query.get(worker.salon_id) if worker.salon_id else None
    
    return jsonify({
        "id": worker.id,
        "name": worker.name,
        "phone": worker.phone,
        "skill": worker.skill,
        "experience": worker.experience,
        "image_url": worker.image_url,
        "salon_id": worker.salon_id,
        "salon_name": salon.name if salon else "No Salon Assigned",
        "is_approved": worker.is_approved
    })

@worker_bp.route('/<int:id>/update', methods=['PUT'])
def update_worker(id):
    worker = Worker.query.get(id)
    if not worker:
        return jsonify({"message": "Worker not found", "status": "error"}), 404
        
    data = request.json
    if 'name' in data:
        worker.name = data['name']
    if 'phone' in data:
        worker.phone = data['phone']
    if 'skill' in data:
        worker.skill = data['skill']
    if 'experience' in data:
        worker.experience = data['experience']
    if 'image_url' in data:
        worker.image_url = data['image_url']
        
    if 'salon_id' in data and data['salon_id']:
        if str(data['salon_id']) != str(worker.salon_id):
            worker.salon_id = data['salon_id']
            worker.is_approved = False  # Need approval from new owner

    db.session.commit()
    return jsonify({
        "message": "Profile updated successfully. If you changed shop, please wait for approval.",
        "status": "success",
        "worker": {
            "id": worker.id,
            "name": worker.name,
            "image_url": worker.image_url,
            "is_approved": worker.is_approved
        }
    })

@worker_bp.route('/<int:id>/upload-photo', methods=['POST'])
def upload_photo(id):
    worker = Worker.query.get(id)
    if not worker:
        return jsonify({"message": "Worker not found", "status": "error"}), 404
        
    if 'photo' not in request.files:
        return jsonify({"message": "No file part", "status": "error"}), 400
        
    file = request.files['photo']
    if file.filename == '':
        return jsonify({"message": "No selected file", "status": "error"}), 400
        
    if file:
        filename = secure_filename(f"worker_{id}_{int(datetime.now().timestamp())}_{file.filename}")
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        worker.image_url = request.host_url + 'static/uploads/' + filename
        db.session.commit()
        
        return jsonify({
            "message": "Photo uploaded successfully",
            "status": "success",
            "image_url": worker.image_url
        })

@worker_bp.route('/<int:id>/toggle-status', methods=['POST'])
def toggle_status(id):
    worker = Worker.query.get(id)
    if not worker:
        return jsonify({"message": "Worker not found", "status": "error"}), 404
    # Toggle online/offline
    worker.status = 'online' if worker.status == 'offline' else 'offline'
    db.session.commit()
    return jsonify({
        "message": f"Status changed to {worker.status}",
        "status": "success",
        "worker_status": worker.status
    })

@worker_bp.route('/earnings/<int:id>', methods=['GET'])
def get_earnings(id):
    from datetime import datetime, timedelta
    worker = db.session.get(Worker, id)
    if not worker:
        return jsonify({"message": "Worker not found", "status": "error"}), 404

    completed = Booking.query.filter_by(worker_id=id, status='completed').all()

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def booking_amount(b):
        try:
            return b.service.price if b.service else 0
        except Exception:
            return 0

    today_earnings = sum(booking_amount(b) for b in completed if b.created_at and b.created_at >= today_start)
    week_earnings  = sum(booking_amount(b) for b in completed if b.created_at and b.created_at >= week_start)
    month_earnings = sum(booking_amount(b) for b in completed if b.created_at and b.created_at >= month_start)
    total_earnings = sum(booking_amount(b) for b in completed)

    # Build last 7 days chart data
    daily_data = []
    for i in range(6, -1, -1):
        day = today_start - timedelta(days=i)
        day_end = day + timedelta(days=1)
        day_total = sum(booking_amount(b) for b in completed if b.created_at and day <= b.created_at < day_end)
        daily_data.append({
            "day": day.strftime('%a'),  # Mon, Tue, etc.
            "amount": day_total
        })

    return jsonify({
        "status": "success",
        "today": today_earnings,
        "this_week": week_earnings,
        "this_month": month_earnings,
        "total": total_earnings,
        "completed_jobs": len(completed),
        "daily_chart": daily_data,
        "worker_status": worker.status
    })

