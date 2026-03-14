from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Salon, Service, Booking, Worker, Offer, Review, Notification, OTPVerification
from sqlalchemy import func
from utils.sms_service import SMSService
from datetime import datetime, timedelta
import random
import string
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests
from config import Config

user_portal_bp = Blueprint('user_portal', __name__, url_prefix='/user-portal')

# ─── Auth Helpers ────────────────────────────────────────────────────────────
def user_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'portal_user_id' not in session:
            flash('Please login to continue.', 'danger')
            return redirect(url_for('user_portal.login'))
        
        user = db.session.get(User, session['portal_user_id'])
        if not user or not user.is_active:
            session.pop('portal_user_id', None)
            flash('Your account has been suspended. Please contact support.', 'danger')
            return redirect(url_for('user_portal.login'))
            
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    return db.session.get(User, session.get('portal_user_id'))

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# ─── Login ────────────────────────────────────────────────────────────────────
@user_portal_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'portal_user_id' in session:
        return redirect(url_for('user_portal.home'))
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        user = User.query.filter_by(phone=phone).first()
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Your account has been suspended. Please contact support.', 'danger')
                return redirect(url_for('user_portal.login'))
            session['portal_user_id'] = user.id
            flash(f'Welcome back, {user.name}! 👋', 'success')
            return redirect(url_for('user_portal.home'))
        flash('Invalid phone or password.', 'danger')
    return render_template('user_portal/login.html')

@user_portal_bp.route('/google-login', methods=['POST'])
def google_login():
    token = request.json.get('credential')
    if not token:
        return jsonify({'success': False, 'message': 'No token provided'}), 400

    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), Config.GOOGLE_CLIENT_ID)
        
        # Get user info from token
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', 'Google User')
        picture = idinfo.get('picture')

        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            # Check by email
            user = User.query.filter_by(email=email).first()
            if user:
                user.google_id = google_id
                if not user.profile_image:
                    user.profile_image = picture
            else:
                # Create new user
                user = User(
                    name=name,
                    email=email,
                    google_id=google_id,
                    profile_image=picture,
                    is_active=True
                )
                db.session.add(user)
            db.session.commit()

        # Login the user
        if not user.is_active:
            return jsonify({'success': False, 'message': 'Account suspended.'}), 403
        
        session['portal_user_id'] = user.id
        return jsonify({'success': True, 'message': 'Login successful'})

    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid token'}), 400

# ─── OTP Login Routes ───────────────────────────────────────────────────────
@user_portal_bp.route('/send-login-otp', methods=['POST'])
def send_login_otp():
    phone = request.form.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Phone number required'}), 400
    
    # Check if user exists
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'success': False, 'message': 'Account not found. Please register first.'}), 404
        
    otp_record = OTPVerification(phone=phone, purpose='login')
    db.session.add(otp_record)
    db.session.commit()
    
    # Send via SMSService
    success, msg = SMSService.send_otp(phone, otp_record.otp, "Saloon Essy Login")
    if success:
        return jsonify({'success': True, 'message': 'OTP sent successfully'})
    return jsonify({'success': False, 'message': f'Failed to send OTP: {msg}'}), 500

@user_portal_bp.route('/verify-login-otp', methods=['POST'])
def verify_login_otp():
    phone = request.form.get('phone')
    otp = request.form.get('otp')
    
    if OTPVerification.verify_otp(phone, otp, purpose='login'):
        user = User.query.filter_by(phone=phone).first()
        if user and user.is_active:
            session['portal_user_id'] = user.id
            return jsonify({'success': True, 'message': 'Login successful'})
        return jsonify({'success': False, 'message': 'User account issue'}), 403
    return jsonify({'success': False, 'message': 'Invalid or expired OTP'}), 401

# ─── Register ────────────────────────────────────────────────────────────────
@user_portal_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        gender = request.form.get('gender')
        if User.query.filter_by(phone=phone).first():
            flash('An account with this phone already exists.', 'danger')
            return render_template('user_portal/register.html')
        user = User(
            name=name,
            phone=phone,
            password=generate_password_hash(password),
            gender=gender
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('user_portal.login'))
    return render_template('user_portal/register.html')

# ─── Home / Browse Salons ────────────────────────────────────────────────────
@user_portal_bp.route('/')
@user_portal_bp.route('/home')
@user_login_required
def home():
    user = get_current_user()
    all_salons = Salon.query.filter_by(is_active=True).all()
    # Show all active salons regardless of current open status
    salons = all_salons
    raw_offers = Offer.query.filter_by(is_active=True).order_by(Offer.created_at.desc()).limit(10).all()
    # Only show offers from salons that are currently open
    active_offers = [o for o in raw_offers if o.salon and o.salon.is_open]
    recent_bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.slot_time.desc()).limit(3).all()
    
    # Fetch top-rated workers using a SQL filter — avoids loading ALL workers into RAM
    top_workers = Worker.query.filter(
        Worker.is_approved == True,
        Worker.is_active == True,
        Worker.rating >= 4.5
    ).limit(15).all()
    random.shuffle(top_workers)
    top_workers = top_workers[:10]

    return render_template('user_portal/home.html',
                           user=user,
                           salons=salons,
                           active_offers=active_offers,
                           top_workers=top_workers,
                           recent_bookings=recent_bookings,
                           now=datetime.now(),
                           active_page='home')

# ─── Salon Detail ─────────────────────────────────────────────────────────────
@user_portal_bp.route('/salon/<int:salon_id>')
@user_login_required
def salon_detail(salon_id):
    user = get_current_user()
    salon = db.session.get(Salon, salon_id)
    if not salon:
        from flask import abort
        abort(404)
    services = Service.query.filter_by(salon_id=salon_id).all()
    workers = Worker.query.filter_by(salon_id=salon_id, is_approved=True).all()
    today = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('user_portal/salon_detail.html',
                           user=user, salon=salon, services=services,
                           workers=workers, today=today, b_model=Booking, active_page='home')

# ─── Book Service ─────────────────────────────────────────────────────────────
@user_portal_bp.route('/book', methods=['POST'])
@user_login_required
def book_service():
    user = get_current_user()
    service_id = request.form.get('service_id')
    salon_id = request.form.get('salon_id')
    worker_id = request.form.get('worker_id')
    slot_date = request.form.get('slot_date')
    slot_time_val = request.form.get('slot_time')

    if not all([service_id, salon_id, slot_date, slot_time_val]):
        flash('Please fill all fields.', 'danger')
        return redirect(request.referrer or url_for('user_portal.home'))

    slot_datetime = datetime.strptime(f"{slot_date} {slot_time_val}", "%Y-%m-%d %H:%M")

    # NEW: Prevent double booking for the same worker
    if worker_id:
        existing_booking = Booking.query.filter_by(
            worker_id=int(worker_id),
            slot_time=slot_datetime
        ).filter(Booking.status.in_(['pending', 'accepted'])).first()
        
        if existing_booking:
            flash('This specialist is already booked for this time. Please choose another slot.', 'warning')
            return redirect(request.referrer or url_for('user_portal.home'))

    # If no worker selected, pick one automatically from the salon
    if not worker_id or worker_id == "":
        potential_workers = Worker.query.filter_by(salon_id=int(salon_id), is_approved=True, is_active=True).all()
        # Filter out busy workers
        available_workers = []
        for w in potential_workers:
            busy = Booking.query.filter_by(worker_id=w.id, slot_time=slot_datetime).filter(Booking.status.in_(['pending', 'accepted'])).first()
            if not busy:
                available_workers.append(w)
        
        if available_workers:
            selected_worker = random.choice(available_workers)
            worker_id = selected_worker.id
        else:
            flash('No specialists available at this exact time. Try a different slot.', 'warning')
            return redirect(request.referrer or url_for('user_portal.home'))

    booking = Booking(
        user_id=user.id,
        salon_id=int(salon_id),
        service_id=int(service_id),
        worker_id=int(worker_id),
        slot_time=slot_datetime,
        status='pending',
        otp=None
    )
    db.session.add(booking)
    db.session.commit()
    
    # 🔔 Add Notification for User
    new_notif = Notification(
        user_id=user.id,
        title="Booking Request Sent 💇",
        message=f"Your request for {booking.service.name} has been sent to the specialist. Waiting for approval.",
        type="booking"
    )
    db.session.add(new_notif)
    db.session.commit()

    # 📱 Send Confirmation SMS
    from utils.sms_service import SMSService
    SMSService.send_booking_confirmation(user.phone, booking.salon.name, slot_datetime.strftime('%d %b, %I:%M %p'))

    flash('Appointment request sent! ⏳ Waiting for your specialist to accept.', 'success')
    return redirect(url_for('user_portal.my_bookings'))

# ─── My Bookings ─────────────────────────────────────────────────────────────
@user_portal_bp.route('/bookings')
@user_login_required
def my_bookings():
    user = get_current_user()
    from datetime import datetime
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.slot_time.desc()).all()
    return render_template('user_portal/bookings.html', user=user, bookings=bookings, active_page='bookings', now=datetime.now(), b_model=Booking)

@user_portal_bp.route('/api/bookings/status')
@user_login_required
def get_bookings_status():
    user_id = session.get('portal_user_id')
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return {b.id: b.status for b in bookings}

# ─── Profile ─────────────────────────────────────────────────────────────────
@user_portal_bp.route('/profile')
@user_login_required
def profile():
    user = get_current_user()
    total_bookings = Booking.query.filter_by(user_id=user.id).count()
    completed = Booking.query.filter_by(user_id=user.id, status='completed').count()
    # Use func.sum() to avoid loading all bookings into RAM
    total_spent = db.session.query(
        func.coalesce(func.sum(Service.price), 0)
    ).join(Booking, Service.id == Booking.service_id).filter(
        Booking.user_id == user.id,
        Booking.status == 'completed'
    ).scalar()
    return render_template('user_portal/profile.html',
                           user=user, total_bookings=total_bookings,
                           completed=completed, total_spent=total_spent,
                           active_page='profile')

# ─── Cancel Booking ───────────────────────────────────────────────────────────
@user_portal_bp.route('/bookings/<int:id>/cancel', methods=['POST'])
@user_login_required
def cancel_booking(id):
    booking = db.session.get(Booking, id)
    if not booking:
        from flask import abort
        abort(404)
    if booking.user_id != session.get('portal_user_id'):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user_portal.my_bookings'))
    if booking.status == 'pending':
        booking.status = 'rejected'
        db.session.commit()
        flash('Booking cancelled.', 'success')
    else:
        flash('Only pending bookings can be cancelled.', 'warning')
    return redirect(url_for('user_portal.my_bookings'))

@user_portal_bp.route('/bookings/<int:id>/payment', methods=['POST'])
@user_login_required
def update_payment(id):
    booking = db.session.get(Booking, id)
    if not booking:
        from flask import abort
        abort(404)
    if booking.user_id != session.get('portal_user_id'):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user_portal.my_bookings'))
    
    method = request.form.get('payment_method')
    if method in ['Cash', 'Online']:
        booking.payment_method = method
        db.session.commit()
        flash(f'Payment method updated to {method}.', 'success')
    
    return redirect(url_for('user_portal.my_bookings'))

# ─── Notifications ───────────────────────────────────────────────────────────
@user_portal_bp.route('/notifications')
@user_login_required
def notifications():
    user = get_current_user()
    from models import Notification
    notifications_list = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(30).all()
    
    # Mark all as read when viewing
    for n in notifications_list:
        n.is_read = True
    db.session.commit()
    
    return render_template('user_portal/notifications.html', user=user, notifications=notifications_list, active_page='notifications')

@user_portal_bp.route('/bookings/<int:id>/rate', methods=['GET', 'POST'])
@user_login_required
def rate_booking(id):
    booking = db.session.get(Booking, id)
    if not booking:
        from flask import abort
        abort(404)
    if booking.user_id != session.get('portal_user_id'):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user_portal.my_bookings'))
    
    if booking.status != 'completed':
        flash('You can only rate completed services.', 'warning')
        return redirect(url_for('user_portal.my_bookings'))

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        # Check if already reviewed
        existing = Review.query.filter_by(booking_id=id).first()
        if existing:
            flash('You have already reviewed this service.', 'info')
            return redirect(url_for('user_portal.my_bookings'))

        review = Review(
            booking_id=id,
            user_id=booking.user_id,
            salon_id=booking.salon_id,
            rating=int(rating),
            comment=comment
        )
        db.session.add(review)
        
        # Update Salon Rating (simplified average)
        salon = db.session.get(Salon, booking.salon_id)
        all_reviews = Review.query.filter_by(salon_id=salon.id).all()
        total_rating = sum(r.rating for r in all_reviews) + int(rating)
        count = len(all_reviews) + 1
        # Explicitly round to 1 decimal place
        salon.rating = float(round(total_rating / count, ndigits=1))

        db.session.commit()
        flash('Thank you for your feedback! ⭐', 'success')
        return redirect(url_for('user_portal.my_bookings'))
        
    return render_template('user_portal/add_review.html', booking=booking)

# ─── Settings & Profile (Original) ───────────────────────────────────────────
@user_portal_bp.route('/settings', methods=['GET', 'POST'])
@user_login_required
def settings():
    user = get_current_user()
    if request.method == 'POST':
        user.name = request.form.get('name')
        # Only update email if not a Google user (Google users have fixed emails)
        if not user.google_id:
            user.email = request.form.get('email')
        
        new_phone = request.form.get('phone')
        if new_phone:
            user.phone = new_phone
        
        # Handle Profile Image Upload
        file = request.files.get('profile_image_file')
        if file and file.filename != '':
            import os
            from werkzeug.utils import secure_filename
            from flask import current_app
            filename = secure_filename(f"user_{user.id}_{file.filename}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'user_profiles')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            user.profile_image = url_for('static', filename=f'uploads/user_profiles/{filename}')
        
        new_password = request.form.get('password')
        if new_password:
            user.password = generate_password_hash(new_password)
            
        db.session.commit()
        flash('Settings updated successfully! ✨', 'success')
        return redirect(url_for('user_portal.settings'))
        
    return render_template('user_portal/settings.html', user=user, active_page='settings')

# ─── Logout ──────────────────────────────────────────────────────────────────
@user_portal_bp.route('/logout')
def logout():
    session.pop('portal_user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('user_portal.login'))
@user_portal_bp.route('/api/check-booking-status')
@user_login_required
def check_booking_status():
    user = get_current_user()
    # Find bookings whose status changed (no longer pending) and hasn't notified user yet
    updated_bookings = Booking.query.filter(
        Booking.user_id == user.id,
        Booking.status != 'pending',
        Booking.user_notified == False
    ).all()
    
    if updated_bookings:
        status_data = []
        for b in updated_bookings:
            b.user_notified = True
            status_data.append({
                "id": b.id,
                "status": b.status,
                "service": b.service.name if b.service else "Service",
                "message": f"Your booking for {b.service.name if b.service else 'Service'} has been {b.status}!"
            })
        db.session.commit()
        return jsonify({"updates": True, "bookings": status_data})
    
    # Check for upcoming reminders (if booking is in next 30 mins)
    upcoming = Booking.query.filter(
        Booking.user_id == user.id,
        Booking.status == 'accepted',
        Booking.slot_time > datetime.utcnow(),
        Booking.slot_time <= datetime.utcnow() + timedelta(minutes=30),
        Booking.user_notified == True # Only remind after it became accepted
    ).all()

    # Note: Using a session variable to prevent spamming reminders for same slot
    reminded_slots = session.get('reminded_slots', [])
    for b in upcoming:
        if b.id not in reminded_slots:
            reminded_slots.append(b.id)
            session['reminded_slots'] = reminded_slots
            return jsonify({
                "updates": True, 
                "bookings": [{
                    "id": b.id,
                    "status": "upcoming",
                    "service": b.service.name,
                    "message": f"Reminder: Your job for {b.service.name} is in less than 30 minutes! ⏰"
                }]
            })
    
    return jsonify({"updates": False})
