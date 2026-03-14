from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models.user_model import SuperAdmin, User, Worker, Owner
from models.salon_model import Salon, Service
from models.booking_model import Booking
from models.review_model import Review
from models.complaint_model import Complaint
from utils.sms_service import SMSService
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def index():
    if current_user.is_authenticated and isinstance(current_user, SuperAdmin):
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and isinstance(current_user, SuperAdmin):
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = SuperAdmin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid admin credentials', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not isinstance(current_user, SuperAdmin):
        return redirect(url_for('admin.login'))
        
    stats = {
        'total_salons': Salon.query.count(),
        'total_users': User.query.count(),
        'total_workers': Worker.query.count(),
        'total_owners': Owner.query.count(),
        'total_bookings': Booking.query.count(),
        'total_revenue': sum(b.service.price for b in Booking.query.filter_by(status='completed').all() if b.service)
    }
    
    recent_salons = Salon.query.order_by(Salon.id.desc()).limit(5).all()
    from flask import current_app
    return render_template('admin/dashboard.html', 
                           stats=stats, 
                           recent_salons=recent_salons, 
                           active_page='dashboard', 
                           config=current_app.config)

@admin_bp.route('/salons')
@login_required
def salons():
    if not isinstance(current_user, SuperAdmin): return redirect(url_for('admin.login'))
    all_salons = Salon.query.all()
    return render_template('admin/salons.html', salons=all_salons, active_page='salons')

@admin_bp.route('/salon/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_salon(id):
    if not isinstance(current_user, SuperAdmin): return jsonify({'success': False}), 403
    salon = db.session.get(Salon, id)
    if not salon:
        from flask import abort
        abort(404)
    salon.is_active = not salon.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': salon.is_active})

@admin_bp.route('/owner/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_owner(id):
    if not isinstance(current_user, SuperAdmin): return jsonify({'success': False}), 403
    owner = db.session.get(Owner, id)
    if not owner:
        from flask import abort
        abort(404)
    owner.is_active = not owner.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': owner.is_active})

@admin_bp.route('/users')
@login_required
def users():
    if not isinstance(current_user, SuperAdmin): return redirect(url_for('admin.login'))
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users, active_page='users')

@admin_bp.route('/user/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_user(id):
    if not isinstance(current_user, SuperAdmin): return jsonify({'success': False}), 403
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': user.is_active})

@admin_bp.route('/workers')
@login_required
def workers():
    if not isinstance(current_user, SuperAdmin): return redirect(url_for('admin.login'))
    all_workers = Worker.query.all()
    return render_template('admin/workers.html', workers=all_workers, active_page='workers')

@admin_bp.route('/worker/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_worker(id):
    if not isinstance(current_user, SuperAdmin): return jsonify({'success': False}), 403
    worker = Worker.query.get_or_404(id)
    worker.is_active = not worker.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': worker.is_active})

@admin_bp.route('/worker/<int:id>/approve', methods=['POST'])
@login_required
def toggle_worker_approval(id):
    if not isinstance(current_user, SuperAdmin): return jsonify({'success': False}), 403
    worker = Worker.query.get_or_404(id)
    worker.is_approved = not worker.is_approved
    db.session.commit()
    return jsonify({'success': True, 'is_approved': worker.is_approved})

@admin_bp.route('/bookings')
@login_required
def bookings():
    if not isinstance(current_user, SuperAdmin): return redirect(url_for('admin.login'))
    all_bookings = Booking.query.order_by(Booking.id.desc()).all()
    return render_template('admin/bookings.html', bookings=all_bookings, active_page='bookings')

@admin_bp.route('/owners')
@login_required
def owners():
    if not isinstance(current_user, SuperAdmin): return redirect(url_for('admin.login'))
    all_owners = Owner.query.all()
    return render_template('admin/owners.html', owners=all_owners, active_page='owners')

@admin_bp.route('/complaints')
@login_required
def complaints():
    if not isinstance(current_user, SuperAdmin): return redirect(url_for('admin.login'))
    all_complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    
    # Enrich data with target names
    for c in all_complaints:
        if c.target_type == 'worker':
            target = Worker.query.get(c.target_id)
            c.target_name = target.name if target else "Deleted Worker"
            c.target_phone = target.phone if target else ""
        else:
            target = Owner.query.get(c.target_id)
            c.target_name = target.name if target else "Deleted Owner"
            c.target_phone = target.phone if target else ""
            
    return render_template('admin/complaints.html', complaints=all_complaints, active_page='complaints')

@admin_bp.route('/complaint/<int:id>/warn', methods=['POST'])
@login_required
def warn_target(id):
    if not isinstance(current_user, SuperAdmin): return jsonify({'success': False}), 403
    complaint = Complaint.query.get_or_404(id)
    
    # Get target phone
    phone = ""
    if complaint.target_type == 'worker':
        target = Worker.query.get(complaint.target_id)
        phone = target.phone if target else ""
    else:
        target = Owner.query.get(complaint.target_id)
        phone = target.phone if target else ""
        
    if phone:
        msg = f"Alert! We have received several complaints about your services: '{complaint.subject}'. Please improve or your account will be blocked. - Saloon Essy Support"
        success, _ = SMSService.send_otp(phone, msg, "Saloon Essy") # Using send_otp as a generic SMS sender for now
        if success:
            complaint.status = 'warned'
            db.session.commit()
            return jsonify({'success': True, 'message': 'Warning sent!'})
            
    return jsonify({'success': False, 'message': 'Could not send message.'})

@admin_bp.route('/complaint/<int:id>/resolve', methods=['POST'])
@login_required
def resolve_complaint(id):
    if not isinstance(current_user, SuperAdmin): return jsonify({'success': False}), 403
    complaint = Complaint.query.get_or_404(id)
    complaint.status = 'resolved'
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.login'))
