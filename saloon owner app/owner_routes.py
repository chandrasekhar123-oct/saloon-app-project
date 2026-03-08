from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Owner, Shop, Service, Worker, Booking, Earnings
from datetime import date

owner_bp = Blueprint('owner', __name__)

@owner_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('owner.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        owner = Owner.query.filter_by(email=email).first()
        
        if owner and check_password_hash(owner.password, password):
            login_user(owner)
            return redirect(url_for('owner.dashboard'))
        flash('Invalid email or password', 'danger')
    
    return render_template('owner/login.html')

@owner_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Register Owner
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        gst = request.form.get('gst')
        
        # 2. Register Shop
        shop_name = request.form.get('shop_name')
        shop_address = request.form.get('shop_address')
        opening_time = request.form.get('opening_time')
        closing_time = request.form.get('closing_time')
        map_url = request.form.get('map_url')
        
        hashed_password = generate_password_hash(password)
        new_owner = Owner(name=name, email=email, phone=phone, password=hashed_password, gst_number=gst)
        
        try:
            db.session.add(new_owner)
            db.session.flush() 
            
            new_shop = Shop(
                owner_id=new_owner.id,
                name=shop_name,
                address=shop_address,
                opening_time=opening_time,
                closing_time=closing_time,
                map_url=map_url
            )
            db.session.add(new_shop)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('owner.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Email or phone might already exist.', 'danger')
            
    return render_template('owner/register.html')

@owner_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    shop = current_user.shop
    if request.method == 'POST':
        shop.name = request.form.get('shop_name')
        shop.address = request.form.get('shop_address')
        shop.opening_time = request.form.get('opening_time')
        shop.closing_time = request.form.get('closing_time')
        shop.map_url = request.form.get('map_url')
        
        db.session.commit()
        flash('Shop profile updated successfully!', 'success')
        return redirect(url_for('owner.dashboard'))
        
    return render_template('owner/edit_profile.html', shop=shop)

@owner_bp.route('/dashboard')
@login_required
def dashboard():
    shop = current_user.shop
    if not shop:
        return "Please register a shop first." 
        
    today_bookings_list = Booking.query.filter_by(shop_id=shop.id).all()
    
    stats = {
        'total_bookings': len(today_bookings_list),
        'completed_services': len([b for b in today_bookings_list if b.status == 'Completed']),
        'cancelled_bookings': len([b for b in today_bookings_list if b.status == 'Cancelled']),
        'today_earnings': sum(b.service.price for b in today_bookings_list if b.status == 'Completed'),
        'monthly_earnings': 45000 
    }
    
    return render_template('owner/dashboard.html', stats=stats, appointments=today_bookings_list)

@owner_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('owner.login'))

@owner_bp.route('/services')
@login_required
def manage_services():
    services = Service.query.filter_by(shop_id=current_user.shop.id).all()
    return render_template('owner/services.html', services=services)

@owner_bp.route('/workers')
@login_required
def manage_workers():
    workers = Worker.query.filter_by(shop_id=current_user.shop.id).all()
    return render_template('owner/workers.html', workers=workers)

@owner_bp.route('/bookings')
@login_required
def bookings():
    shop = current_user.shop
    appointments = Booking.query.filter_by(shop_id=shop.id).order_by(Booking.slot_time.desc()).all()
    return render_template('owner/dashboard.html', stats={'total_bookings': len(appointments), 'completed_services': 0, 'cancelled_bookings': 0, 'today_earnings': 0, 'monthly_earnings': 0}, appointments=appointments)

@owner_bp.route('/earnings')
@login_required
def earnings():
    return "Earnings feature coming soon."

@owner_bp.route('/profile')
@login_required
def profile():
    return render_template('owner/profile.html', shop=current_user.shop)
