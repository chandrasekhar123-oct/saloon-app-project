from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models.user_model import SuperAdmin, User, Worker
from models.salon_model import Salon, Service
from models.booking_model import Booking
from models.review_model import Review
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

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
        'total_bookings': Booking.query.count(),
        'total_revenue': sum(b.service.price for b in Booking.query.filter_by(status='completed').all() if b.service)
    }
    
    recent_salons = Salon.query.order_by(Salon.id.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_salons=recent_salons, active_page='dashboard')

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
    salon = Salon.query.get_or_404(id)
    salon.is_active = not salon.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': salon.is_active})

@admin_bp.route('/users')
@login_required
def users():
    if not isinstance(current_user, SuperAdmin): return redirect(url_for('admin.login'))
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users, active_page='users')

@admin_bp.route('/workers')
@login_required
def workers():
    if not isinstance(current_user, SuperAdmin): return redirect(url_for('admin.login'))
    all_workers = Worker.query.all()
    return render_template('admin/workers.html', workers=all_workers, active_page='workers')

@admin_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.login'))
