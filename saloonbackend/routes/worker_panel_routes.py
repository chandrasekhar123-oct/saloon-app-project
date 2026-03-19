from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify, abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models import db, Worker, Booking, Salon, Review, Notification
from datetime import datetime, timedelta
from functools import wraps
import os
import random
import string
import secrets
import hmac
from google.oauth2 import id_token
from google.auth.transport import requests
from config import Config
from services.revenue_service import calculate_revenue_split

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

worker_panel_bp = Blueprint('worker_panel', __name__, url_prefix='/worker-panel')

# ─── Auth Helpers ────────────────────────────────────────────────────────────
def worker_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'worker_id' not in session:
            flash('Please login first.', 'danger')
            return redirect(url_for('worker_panel.login'))
        
        # Check approval status and active status from DB on every request
        worker = Worker.query.get(session['worker_id'])
        if not worker:
            session.pop('worker_id', None)
            return redirect(url_for('worker_panel.login'))
            
        if not worker.is_active:
            session.pop('worker_id', None)
            flash('Your account has been deactivated by the administrator.', 'danger')
            return redirect(url_for('worker_panel.login'))

        if not worker.is_approved:
            session.pop('worker_id', None)
            flash('Your account is pending approval by the shop owner.', 'warning')
            return redirect(url_for('worker_panel.login'))

        # NEW: Ensure Google users select a salon before accessing dashboard
        if not worker.salon_id and request.endpoint != 'worker_panel.setup_profile':
            flash('Please complete your profile by selecting a salon.', 'info')
            return redirect(url_for('worker_panel.setup_profile'))
            
        return f(*args, **kwargs)
    return decorated

def get_current_worker():
    return Worker.query.get(session.get('worker_id'))

# ─── Login ────────────────────────────────────────────────────────────────────
@worker_panel_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'worker_id' in session:
        return redirect(url_for('worker_panel.dashboard'))

    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        worker = Worker.query.filter_by(phone=phone).first()

        if worker and check_password_hash(worker.password, password):
            if not worker.is_active:
                flash('Your account is deactivated. Contact admin.', 'danger')
                return redirect(url_for('worker_panel.login'))
            if not worker.is_approved:
                flash('Your account is pending approval by the shop owner. Please wait.', 'warning')
                return redirect(url_for('worker_panel.login'))
            session['worker_id'] = worker.id
            session['show_approval_notif'] = True  # Show approval banner on first dashboard visit
            flash(f'Welcome back, {worker.name}!', 'success')
            return redirect(url_for('worker_panel.dashboard'))
        else:
            flash('Invalid phone or password.', 'danger')

    return render_template('worker/login.html')

@worker_panel_bp.route('/google-login', methods=['POST'])
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
        name = idinfo.get('name', 'Google Worker')
        picture = idinfo.get('picture')

        # Check if worker exists
        worker = Worker.query.filter_by(google_id=google_id).first()
        if not worker:
            # Check by email
            worker = Worker.query.filter_by(email=email).first()
            if worker:
                worker.google_id = google_id
                if not worker.image_url:
                    worker.image_url = picture
            else:
                # Create new worker (Unlinked to a salon initially)
                worker = Worker(
                    name=name,
                    email=email,
                    google_id=google_id,
                    image_url=picture,
                    is_active=True,
                    is_approved=True 
                )
                db.session.add(worker)
            db.session.commit()

        # Login the worker
        if not worker.is_active:
            return jsonify({'success': False, 'message': 'Account deactivated.'}), 403
        
        session['worker_id'] = worker.id
        
        # Determine redirection
        if not worker.salon_id:
            return jsonify({'success': True, 'message': 'New account', 'redirect': url_for('worker_panel.setup_profile')})
        
        return jsonify({'success': True, 'message': 'Login successful', 'redirect': url_for('worker_panel.dashboard')})

    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid token'}), 400

# ─── Profile Setup (For Google/New Workers) ──────────────────────────────────
@worker_panel_bp.route('/setup-profile', methods=['GET', 'POST'])
def setup_profile():
    if 'worker_id' not in session: return redirect(url_for('worker_panel.login'))
    worker = get_current_worker()
    salons = Salon.query.all()
    
    if request.method == 'POST':
        worker.salon_id = request.form.get('salon_id')
        worker.experience = request.form.get('experience')
        worker.skill = request.form.get('skill')
        worker.gender = request.form.get('gender')
        db.session.commit()
        flash('Profile completed! Welcome to the team.', 'success')
        return redirect(url_for('worker_panel.dashboard'))
        
    return render_template('worker/setup_profile.html', worker=worker, salons=salons)

# ─── Register ────────────────────────────────────────────────────────────────
@worker_panel_bp.route('/register', methods=['GET', 'POST'])
def register():
    salons = Salon.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        gender = request.form.get('gender')
        state = request.form.get('state')
        city = request.form.get('city')
        salon_id = request.form.get('salon_id')
        experience = request.form.get('experience')
        skill = request.form.get('skill')

        worker = Worker(
            name=name,
            phone=phone,
            password=generate_password_hash(password),
            gender=gender,
            state=state,
            city=city,
            salon_id=int(salon_id) if salon_id else None,
            experience=int(experience) if experience else 0,
            skill=skill,
            is_approved=True  # Auto-approved by default
        )
        db.session.add(worker)
        db.session.commit()
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('worker_panel.login'))

    return render_template('worker/register.html', salons=salons)

@worker_panel_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        phone = request.form.get('phone')
        worker = Worker.query.filter_by(phone=phone).first()
        if worker:
            reset_token = secrets.token_urlsafe(32)
            worker.reset_token = reset_token
            db.session.commit()
            flash('A password reset link has been generated. Redirecting...', 'info')
            return redirect(url_for('worker_panel.reset_password', token=reset_token))
        flash('No worker found with this phone number.', 'danger')
    return render_template('worker/forgot_password.html')

@worker_panel_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    worker = Worker.query.filter_by(reset_token=token).first_or_404()
    if request.method == 'POST':
        new_password = request.form.get('password')
        worker.password = generate_password_hash(new_password)
        worker.reset_token = None  # Invalidate token after use
        db.session.commit()
        flash('Password reset successful! Please login.', 'success')
        return redirect(url_for('worker_panel.login'))
    return render_template('worker/reset_password.html', worker=worker)

# ─── Dashboard ───────────────────────────────────────────────────────────────
@worker_panel_bp.route('/')
@worker_panel_bp.route('/dashboard')
@worker_login_required
def dashboard():
    worker = get_current_worker()
    salon = db.session.get(Salon, worker.salon_id) if worker.salon_id else None
    all_bookings = Booking.query.filter_by(worker_id=worker.id).all()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    pending_count = sum(1 for b in all_bookings if b.status == 'pending')
    completed_count = sum(1 for b in all_bookings if b.status == 'completed')
    
    # Calculate Worker's Net Earnings (Share after commission)
    total_completed_bookings = [b for b in all_bookings if b.status == 'completed']
    
    def get_worker_share_est(b, w):
        if not b.service: return 0.0
        if b.commission_applied: return b.worker_share
        # Fallback logic identical to verify_otp
        if w.is_owner or w.payment_type == 'salary': return 0.0
        rate = w.commission_rate or 50.0
        return (rate / 100.0) * float(b.service.price)

    today_earnings = sum(get_worker_share_est(b, worker) 
                         for b in total_completed_bookings if b.slot_time >= today)
    
    upcoming_bookings = [b for b in all_bookings if b.status in ('pending', 'accepted')]
    
    # Calculate Weekly Earnings for Chart (Net share)
    weekly_earnings = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_end = day + timedelta(days=1)
        day_total = sum(get_worker_share_est(b, worker)
                        for b in total_completed_bookings if day <= b.slot_time < day_end)
        weekly_earnings.append({
            'day': day.strftime('%a'),
            'amount': float(round(float(day_total), 2)),
            'percent': int(min(100, int((float(day_total) / 1000.0 * 100.0)))) if day_total > 0 else 5 # Adjusted goal for worker share
        })

    # Success Rate & Monthly
    total_completed = completed_count
    total_jobs = len(all_bookings)
    if total_jobs > 0:
        success_rate = float("{:.1f}".format(float(total_completed) * 100.0 / total_jobs))
    else:
        success_rate = 100.0
    
    # Calculate Average Rating from Reviews
    reviews = Review.query.join(Booking).filter(Booking.worker_id == worker.id).all()
    if reviews:
        avg_rating = float(round(float(sum(r.rating for r in reviews)) / len(reviews), 1))
    else:
        avg_rating = 5.0
    
    month_start = today.replace(day=1)
    month_earnings = sum(get_worker_share_est(b, worker)
                          for b in total_completed_bookings if b.slot_time >= month_start and b.service)

    # Calculate Today's Cash Collection (Total service price for cash bookings)
    today_cash_collection = sum(float(b.service.price) for b in total_completed_bookings 
                                if b.slot_time >= today and b.payment_method == 'Cash' and b.service)

    # Show approval notification once, then clear it
    show_approval_notif = session.pop('show_approval_notif', False)

    return render_template('worker/dashboard.html',
                           worker=worker,
                           salon=salon,
                           pending_count=pending_count,
                           completed_count=completed_count,
                           today_earnings=today_earnings,
                           month_earnings=month_earnings,
                           today_cash_collection=today_cash_collection,
                           weekly_earnings=weekly_earnings,
                           success_rate=success_rate,
                           avg_rating=avg_rating,
                           upcoming_bookings=upcoming_bookings,
                           show_approval_notif=show_approval_notif,
                           now=datetime.now(),
                           active_page='dashboard')

# ─── My Bookings ─────────────────────────────────────────────────────────────
@worker_panel_bp.route('/jobs')
@worker_login_required
def my_bookings():
    worker = get_current_worker()
    bookings = Booking.query.filter_by(worker_id=worker.id).order_by(Booking.slot_time.desc()).all()
    return render_template('worker/bookings.html', worker=worker, bookings=bookings, active_page='bookings')

# ─── Insights / Performance ──────────────────────────────────────────────────
@worker_panel_bp.route('/insights')
@worker_login_required
def insights():
    worker = get_current_worker()
    all_bookings = Booking.query.filter_by(worker_id=worker.id).all()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate stats
    total_jobs = len(all_bookings)
    completed_jobs = [b for b in all_bookings if b.status == 'completed']
    total_completed = len(completed_jobs)
    
    def get_worker_share_est(b, w):
        if not b.service: return 0.0
        if b.commission_applied: return b.worker_share
        if w.is_owner or w.payment_type == 'salary': return 0.0
        rate = w.commission_rate or 50.0
        return (rate / 100.0) * float(b.service.price)

    # Calculate Worker's Net Earnings
    total_earnings = sum(get_worker_share_est(b, worker) for b in completed_jobs)
    
    if total_jobs > 0:
        val = float(total_completed) * 100.0 / total_jobs
        success_rate = float("{:.1f}".format(val))
    else:
        success_rate = 100.0
    
    # Average Rating
    reviews = Review.query.join(Booking).filter(Booking.worker_id == worker.id).all()
    if reviews:
        avg_rating = float(round(float(sum(r.rating for r in reviews)) / len(reviews), 1))
    else:
        avg_rating = 5.0
    
    # Calculate Weekly Trend for Chart (Net share)
    weekly_trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_end = day + timedelta(days=1)
        day_total = sum(get_worker_share_est(b, worker)
                        for b in completed_jobs if day <= b.slot_time < day_end)
        weekly_trend.append({
            'day': day.strftime('%a'),
            'amount': float(round(float(day_total), 2)),
            'percent': int(min(100, int((float(day_total) / 1000.0 * 100.0)))) if day_total > 0 else 5
        })
    
    return render_template('worker/insights.html', 
                           worker=worker, 
                           total_jobs=total_jobs,
                           total_completed=total_completed,
                           total_earnings=total_earnings,
                           success_rate=success_rate,
                           avg_rating=avg_rating,
                           weekly_trend=weekly_trend,
                           active_page='insights')

# ─── Accept Booking ──────────────────────────────────────────────────────────
@worker_panel_bp.route('/jobs/<int:id>/accept', methods=['POST'])
@worker_login_required
def accept_booking(id):
    booking = Booking.query.get_or_404(id)
    # IDOR check: ensure this booking belongs to the current worker
    if booking.worker_id != session.get('worker_id'):
        abort(403)
    otp = secrets.token_hex(3).upper()  # Cryptographically secure 6-char hex OTP
    booking.status = 'accepted'
    booking.otp = otp

    # Allow custom message from worker
    custom_msg = request.form.get('message')
    if custom_msg:
        booking.worker_message = custom_msg
    else:
        # BUSY NOTIFICATION (RAPIDO STYLE)
        worker_id = session.get('worker_id')
        active_jobs = Booking.query.filter_by(worker_id=worker_id, status='accepted').order_by(Booking.slot_time).all()
        # If there's already an accepted job (not counting this one)
        if len(active_jobs) > 1:
            # The first in list is the "Active" one
            first_job = active_jobs[0]
            booking.worker_message = f"Please wait some time, I am finishing a {first_job.service.name}. Don't cancel, please come to our shop shortly!"

    db.session.commit()
    
    # 🔔 Notify User
    new_notif = Notification(
        user_id=booking.user_id,
        title="Booking Accepted! ✅",
        message=f"Good news! Your booking for {booking.service.name} at {booking.salon.name} has been accepted.",
        type="booking"
    )
    db.session.add(new_notif)
    db.session.commit()
    
    # 📱 Send REAL SMS to Customer
    from utils.sms_service import SMSService
    customer_phone = booking.user.phone
    SMSService.send_otp(customer_phone, otp, booking.salon.name)

    flash(f'Booking accepted! OTP {otp} has been sent to the customer.', 'success')
    return redirect(url_for('worker_panel.my_bookings'))

# ─── Reject Booking ──────────────────────────────────────────────────────────
@worker_panel_bp.route('/jobs/<int:id>/reject', methods=['POST'])
@worker_login_required
def reject_booking(id):
    booking = Booking.query.get_or_404(id)
    # IDOR check
    if booking.worker_id != session.get('worker_id'):
        abort(403)
    booking.status = 'rejected'
    db.session.commit()

    # 🔔 Notify User
    new_notif = Notification(
        user_id=booking.user_id,
        title="Booking Rejected ❌",
        message=f"We're sorry, your booking for {booking.service.name} at {booking.salon.name} could not be accepted at this time.",
        type="booking"
    )
    db.session.add(new_notif)
    db.session.commit()
    flash('Booking rejected.', 'danger')
    return redirect(url_for('worker_panel.my_bookings'))

# ─── Verify OTP ──────────────────────────────────────────────────────────────
@worker_panel_bp.route('/jobs/<int:id>/verify-otp', methods=['POST'])
@worker_login_required
def verify_otp(id):
    booking = Booking.query.get_or_404(id)
    # IDOR check
    if booking.worker_id != session.get('worker_id'):
        abort(403)
    otp = request.form.get('otp')
    pay_method = request.form.get('payment_method', 'Cash')
    if booking.otp and hmac.compare_digest(booking.otp, otp):
        booking.status = 'completed'
        booking.payment_method = pay_method
        booking.payment_status = 'Paid'
        
        # Use centralised revenue split service
        split = calculate_revenue_split(booking)
        booking.worker_share = split['worker_amt']
        booking.owner_share = split['owner_amt']
        booking.commission_applied = True
        
        if booking.worker:
            booking.worker.total_earnings = (booking.worker.total_earnings or 0.0) + split['worker_amt']
            booking.worker.current_balance = (booking.worker.current_balance or 0.0) + split['worker_amt']
            
        db.session.commit()
        flash('OTP verified! Service marked as completed. 🎉', 'success')
    else:
        flash('Invalid OTP. Please try again.', 'danger')
    return redirect(url_for('worker_panel.my_bookings'))

# ─── Send Message to Customer ──────────────────────────────────────────────
@worker_panel_bp.route('/jobs/<int:id>/message', methods=['POST'])
@worker_login_required
def send_message(id):
    booking = Booking.query.get_or_404(id)
    msg = request.form.get('message')
    booking.worker_message = msg
    db.session.commit()
    flash('Message sent to customer!', 'success')
    return redirect(url_for('worker_panel.my_bookings'))

# ─── Settings & Profile ────────────────────────────────────────────────────────
@worker_panel_bp.route('/profile', methods=['GET', 'POST'])
@worker_panel_bp.route('/settings', methods=['GET', 'POST'])
@worker_login_required
def settings():
    worker = get_current_worker()
    salon = Salon.query.get(worker.salon_id) if worker.salon_id else None
    
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            worker.name = name
            
        # Only update email if not a Google user
        if not worker.google_id:
            email = request.form.get('email')
            if email:
                worker.email = email

        phone = request.form.get('phone')
        if phone:
            worker.phone = phone
        elif worker.google_id:
            # For Google users, phone is optional
            pass
            
        experience = request.form.get('experience')
        if experience is not None and experience != '':
            worker.experience = int(experience)
        
        state = request.form.get('state')
        if state:
            worker.state = state
            
        city = request.form.get('city')
        if city:
            worker.city = city

        upi_id = request.form.get('upi_id')
        if upi_id:
            worker.upi_id = upi_id

        instagram_url = request.form.get('instagram_url')
        if instagram_url:
            worker.instagram_url = instagram_url

        facebook_url = request.form.get('facebook_url')
        if facebook_url:
            worker.facebook_url = facebook_url
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                if not allowed_file(file.filename):
                    flash('Invalid file type. Allowed: png, jpg, jpeg, webp, gif', 'danger')
                    return redirect(url_for('worker_panel.settings'))
                filename = secure_filename(f"worker_{worker.id}_{int(datetime.now().timestamp())}_{file.filename}")
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                worker.image_url = request.host_url.rstrip('/') + url_for('static', filename=f"uploads/{filename}")
            
        # Fallback to URL text field if no file is uploaded but image_url is provided
        image_url = request.form.get('image_url')
        if image_url and 'photo' not in request.files:
            worker.image_url = image_url
            
        # Saloon Change Option
        salon_id = request.form.get('salon_id')
        if salon_id and str(salon_id) != str(worker.salon_id):
            worker.salon_id = int(salon_id)
            worker.is_approved = False
            flash('Shop changed successfully. Please wait for the new shop owner to approve you.', 'warning')
        
        # New State/City fields
        worker.state = request.form.get('state')
        worker.city = request.form.get('city')
        
        # Handle multiple checkboxes for skills
        skills_list = request.form.getlist('skill_list')
        if skills_list:
            worker.skill = ', '.join(skills_list)
        else:
            worker.skill = request.form.get('skill', '')
            
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('worker_panel.settings'))
        
    total_jobs = Booking.query.filter_by(worker_id=worker.id).count()
    salons = Salon.query.all()
    return render_template('worker/profile.html', worker=worker, salon=salon, salons=salons, total_jobs=total_jobs, active_page='profile')

# ─── Logout ──────────────────────────────────────────────────────────────────
@worker_panel_bp.route('/logout')
def logout():
    session.pop('worker_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('worker_panel.login'))

@worker_panel_bp.route('/toggle_status', methods=['POST'])
@worker_login_required
def toggle_status():
    worker = get_current_worker()
    if not worker:
        return jsonify({'success': False, 'message': 'Worker not found'}), 404
        
    worker.is_active = not worker.is_active
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'is_active': worker.is_active,
    })
@worker_panel_bp.route('/api/check-new-bookings')
@worker_login_required
def check_new_bookings():
    worker = get_current_worker()
    # Find bookings that are pending and haven't triggered a sound yet
    new_bookings = Booking.query.filter_by(worker_id=worker.id, status='pending', worker_notified=False).all()
    
    if new_bookings:
        # Mark them as notified so the sound only plays once
        for b in new_bookings:
            b.worker_notified = True
        db.session.commit()
        return jsonify({"new_jobs": True, "count": len(new_bookings)})
    
    return jsonify({"new_jobs": False})
