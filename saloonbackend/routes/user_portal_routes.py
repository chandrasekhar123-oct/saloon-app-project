from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Salon, Service, Booking, Worker, Offer, Review
from datetime import datetime, timedelta
import random
import string
from functools import wraps

user_portal_bp = Blueprint('user_portal', __name__, url_prefix='/user-portal')

# ─── Auth Helpers ────────────────────────────────────────────────────────────
def user_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'portal_user_id' not in session:
            flash('Please login to continue.', 'danger')
            return redirect(url_for('user_portal.login'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    return User.query.get(session.get('portal_user_id'))

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
            session['portal_user_id'] = user.id
            flash(f'Welcome back, {user.name}! 👋', 'success')
            return redirect(url_for('user_portal.home'))
        flash('Invalid phone or password.', 'danger')
    return render_template('user_portal/login.html')

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
    # Only show salons that are currently open
    salons = [s for s in all_salons if s.is_open]
    raw_offers = Offer.query.filter_by(is_active=True).order_by(Offer.created_at.desc()).limit(10).all()
    # Only show offers from salons that are currently open
    active_offers = [o for o in raw_offers if o.salon and o.salon.is_open]
    recent_bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.slot_time.desc()).limit(3).all()
    return render_template('user_portal/home.html',
                           user=user,
                           salons=salons,
                           offers=active_offers,
                           recent_bookings=recent_bookings,
                           now=datetime.now(),
                           active_page='home')

# ─── Salon Detail ─────────────────────────────────────────────────────────────
@user_portal_bp.route('/salon/<int:salon_id>')
@user_login_required
def salon_detail(salon_id):
    user = get_current_user()
    salon = Salon.query.get_or_404(salon_id)
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

    # If no worker selected, pick one automatically from the salon
    if not worker_id or worker_id == "":
        potential_workers = Worker.query.filter_by(salon_id=int(salon_id), is_approved=True, is_active=True).all()
        if not potential_workers:
            potential_workers = Worker.query.filter_by(salon_id=int(salon_id), is_approved=True).all()
        
        if potential_workers:
            selected_worker = random.choice(potential_workers)
            worker_id = selected_worker.id
        else:
            flash('This salon has no available specialists at the moment. Please try again later.', 'danger')
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
    total_spent = sum(b.service.price for b in Booking.query.filter_by(user_id=user.id, status='completed').all() if b.service)
    return render_template('user_portal/profile.html',
                           user=user, total_bookings=total_bookings,
                           completed=completed, total_spent=total_spent,
                           active_page='profile')

# ─── Cancel Booking ───────────────────────────────────────────────────────────
@user_portal_bp.route('/bookings/<int:id>/cancel', methods=['POST'])
@user_login_required
def cancel_booking(id):
    booking = Booking.query.get_or_404(id)
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
    booking = Booking.query.get_or_404(id)
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
    # Simple notifications based on booking status changes
    notifications_list = Booking.query.filter_by(user_id=user.id).order_by(Booking.slot_time.desc()).limit(20).all()
    return render_template('user_portal/notifications.html', user=user, notifications=notifications_list, active_page='notifications')

@user_portal_bp.route('/bookings/<int:id>/rate', methods=['GET', 'POST'])
@user_login_required
def rate_booking(id):
    booking = Booking.query.get_or_404(id)
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
        salon = Salon.query.get(booking.salon_id)
        all_reviews = Review.query.filter_by(salon_id=salon.id).all()
        total_rating = sum(r.rating for r in all_reviews) + int(rating)
        count = len(all_reviews) + 1
        salon.rating = round(total_rating / count, 1)

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
        user.phone = request.form.get('phone')
        
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
