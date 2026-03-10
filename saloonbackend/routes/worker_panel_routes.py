from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from models import db, Worker, Booking, Salon
from datetime import datetime
from functools import wraps

worker_panel_bp = Blueprint('worker_panel', __name__, url_prefix='/worker-panel')

# ─── Auth Helpers ────────────────────────────────────────────────────────────
def worker_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'worker_id' not in session:
            flash('Please login first.', 'danger')
            return redirect(url_for('worker_panel.login'))
        
        # Check approval status from DB on every request
        worker = Worker.query.get(session['worker_id'])
        if not worker or not worker.is_approved:
            session.pop('worker_id', None)
            flash('Your account is pending approval by the shop owner.', 'warning')
            return redirect(url_for('worker_panel.login'))
            
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

# ─── Register ────────────────────────────────────────────────────────────────
@worker_panel_bp.route('/register', methods=['GET', 'POST'])
def register():
    salons = Salon.query.all()
    if request.method == 'POST':
        from werkzeug.security import generate_password_hash
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        salon_id = request.form.get('salon_id')
        experience = request.form.get('experience', 0)
        skill = request.form.get('skill')

        gender = request.form.get('gender')
        state = request.form.get('state')
        city = request.form.get('city')

        if Worker.query.filter_by(phone=phone).first():
            flash('A worker with this phone already exists.', 'danger')
            return render_template('worker/register.html', salons=salons)

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
            return redirect(url_for('worker_panel.reset_password', worker_id=worker.id))
        flash('No worker found with this phone number.', 'danger')
    return render_template('worker/forgot_password.html')

@worker_panel_bp.route('/reset-password/<int:worker_id>', methods=['GET', 'POST'])
def reset_password(worker_id):
    from werkzeug.security import generate_password_hash
    worker = Worker.query.get_or_404(worker_id)
    if request.method == 'POST':
        new_password = request.form.get('password')
        worker.password = generate_password_hash(new_password)
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
    salon = Salon.query.get(worker.salon_id) if worker.salon_id else None
    all_bookings = Booking.query.filter_by(worker_id=worker.id).all()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    pending_count = sum(1 for b in all_bookings if b.status == 'pending')
    completed_count = sum(1 for b in all_bookings if b.status == 'completed')
    today_earnings = sum(b.service.price for b in all_bookings if b.status == 'completed' and b.slot_time >= today and b.service)
    upcoming_bookings = [b for b in all_bookings if b.status in ('pending', 'accepted')]

    # Show approval notification once, then clear it
    show_approval_notif = session.pop('show_approval_notif', False)

    return render_template('worker/dashboard.html',
                           worker=worker,
                           salon=salon,
                           pending_count=pending_count,
                           completed_count=completed_count,
                           today_earnings=today_earnings,
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
    
    # Calculate stats
    total_jobs = len(all_bookings)
    completed_jobs = [b for b in all_bookings if b.status == 'completed']
    total_completed = len(completed_jobs)
    total_earnings = sum(b.service.price for b in completed_jobs)
    
    success_rate = (total_completed / total_jobs * 100) if total_jobs > 0 else 100
    
    # Simple monthly breakdown (mock logic)
    monthly_data = {
        'count': total_completed,
        'revenue': total_earnings
    }
    
    return render_template('worker/insights.html', 
                           worker=worker, 
                           total_jobs=total_jobs,
                           total_completed=total_completed,
                           total_earnings=total_earnings,
                           success_rate=round(success_rate, 1),
                           active_page='insights')

# ─── Accept Booking ──────────────────────────────────────────────────────────
@worker_panel_bp.route('/jobs/<int:id>/accept', methods=['POST'])
@worker_login_required
def accept_booking(id):
    booking = Booking.query.get_or_404(id)
    import random, string
    otp = ''.join(random.choices(string.digits, k=6))
    booking.status = 'accepted'
    booking.otp = otp  # Generate OTP only when worker accepts

    # BUSY NOTIFICATION (RAPIDO STYLE)
    worker_id = session.get('worker_id')
    active_jobs = Booking.query.filter_by(worker_id=worker_id, status='accepted').order_by(Booking.slot_time).all()
    # If there's already an accepted job (not counting this one)
    if len(active_jobs) > 1:
        # The first in list is the "Active" one
        first_job = active_jobs[0]
        duration = first_job.service.duration or 30
        booking.worker_message = f"Please wait some time, I am finishing a {first_job.service.name}. Don't cancel, please come to our shop shortly!"

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
    booking.status = 'rejected'
    db.session.commit()
    flash('Booking rejected.', 'danger')
    return redirect(url_for('worker_panel.my_bookings'))

# ─── Verify OTP ──────────────────────────────────────────────────────────────
@worker_panel_bp.route('/jobs/<int:id>/verify-otp', methods=['POST'])
@worker_login_required
def verify_otp(id):
    booking = Booking.query.get_or_404(id)
    otp = request.form.get('otp')
    if booking.otp == otp:
        booking.status = 'completed'
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
        worker.name = request.form.get('name')
        worker.phone = request.form.get('phone')
        worker.experience = request.form.get('experience', type=int)
        
        from werkzeug.utils import secure_filename
        import os
        from flask import current_app

        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
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
    from flask import jsonify
    worker = get_current_worker()
    if not worker:
        return jsonify({'success': False, 'message': 'Worker not found'}), 404
        
    worker.is_active = not worker.is_active
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'is_active': worker.is_active,
    })
