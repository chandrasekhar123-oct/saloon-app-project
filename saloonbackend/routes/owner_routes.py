from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Owner, Salon, Service, Worker, Booking, Offer
from datetime import datetime, time, timedelta
import os

owner_bp = Blueprint('owner', __name__)

# ─── API ENDPOINTS (JSON) ──────────────────────────────────────────

@owner_bp.route('/api/bookings/<int:salon_id>', methods=['GET'])
def get_salon_bookings_api(salon_id):
    bookings = Booking.query.filter_by(salon_id=salon_id).all()
    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "user_name": b.user.name,
            "worker_name": b.worker.name,
            "service_name": b.service.name,
            "status": b.status,
            "slot_time": b.slot_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result)

# ─── HELPERS ──────────────────────────────────────────────────────

def get_salon_stats(salon):
    bookings_list = Booking.query.filter_by(salon_id=salon.id).all()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_bookings = len(bookings_list)
    completed_bookings = [b for b in bookings_list if b.status == 'completed']
    success_rate = f"{int((len(completed_bookings) / total_bookings * 100)) if total_bookings > 0 else 100}%"
    
    # Calculate Total Revenue vs Owner Share
    total_revenue = sum(b.service.price for b in completed_bookings if b.service)
    
    # Precise calculation based on applied commissions or default 50%
    owner_earnings = 0.0
    for b in completed_bookings:
        if not b.service: continue
        if b.commission_applied:
            owner_earnings += b.owner_share
        else:
            # Fallback estimation if commission wasn't explicitly recorded
            if b.worker and b.worker.is_owner:
                owner_earnings += b.service.price
            else:
                owner_earnings += (b.service.price * 0.5)
    
    today_completed = [b for b in completed_bookings if b.slot_time >= today]
    today_owner_earnings = sum(b.owner_share if b.commission_applied else (b.service.price * 0.5) for b in today_completed if b.service)

    return {
        'total_bookings': total_bookings,
        'today_bookings': len([b for b in bookings_list if b.slot_time >= today]),
        'completed_services': len(completed_bookings),
        'pending_bookings': len([b for b in bookings_list if b.status == 'pending']),
        'today_revenue': sum(b.service.price for b in today_completed if b.service),
        'today_earnings': today_owner_earnings, # Owner's share
        'total_revenue': total_revenue,
        'owner_total': owner_earnings,
        'active_workers': Worker.query.filter_by(salon_id=salon.id).count(),
        'service_count': Service.query.filter_by(salon_id=salon.id).count(),
        'client_count': len(set([b.user_id for b in bookings_list])),
        'success_rate': success_rate
    }

# ─── WEB INTERFACE (HTML) ──────────────────────────────────────────

@owner_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Check if the user is an Owner
        if isinstance(current_user, Owner):
            return redirect(url_for('owner.dashboard'))
    
    if request.method == 'POST':
        # Check if they are sending JSON (from app) or Form (from web)
        if request.is_json:
            data = request.json
            phone = data.get('phone')
            password = data.get('password')
            owner = Owner.query.filter_by(phone=phone).first()
            if owner and check_password_hash(owner.password, password):
                if not owner.is_active:
                    return jsonify({"message": "Your account has been suspended. Please contact the Super Admin.", "status": "suspended"}), 403
                return jsonify({"message": "Owner login successful", "status": "success", "owner_id": owner.id})
            return jsonify({"message": "Invalid credentials", "status": "error"}), 401
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            owner = Owner.query.filter_by(email=email).first()
            if owner and check_password_hash(owner.password, password):
                if not owner.is_active:
                    flash('Your account has been suspended. Please contact the Super Admin.', 'danger')
                    return redirect(url_for('owner.login'))
                login_user(owner)
                return redirect(url_for('owner.dashboard'))
            flash('Invalid email or password', 'danger')
    
    return render_template('owner/login.html')

@owner_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        gender = request.form.get('gender')
        
        shop_name = request.form.get('shop_name')
        # Get multiple categories from the form
        categories = request.form.getlist('category')
        category_str = ", ".join(categories) if categories else 'Barber Shop'
        shop_address = request.form.get('shop_address')
        state = request.form.get('state')
        location = request.form.get('city') # Getting city and storing in location
        opening_time = request.form.get('opening_time')
        closing_time = request.form.get('closing_time')
        map_url = request.form.get('map_url')
        
        hashed_password = generate_password_hash(password)
        new_owner = Owner(name=name, email=email, phone=phone, password=hashed_password, gender=gender)
        
        try:
            # Check if phone or email already exists to give a better message
            if Owner.query.filter_by(phone=phone).first():
                flash('This phone number is already registered. Please login or use another number.', 'danger')
                return redirect(url_for('owner.register'))
            if Owner.query.filter_by(email=email).first():
                flash('This email is already registered. Please login or use another email.', 'danger')
                return redirect(url_for('owner.register'))

            db.session.add(new_owner)
            db.session.flush() 
            
            new_salon = Salon(
                owner_id=new_owner.id,
                name=shop_name,
                category=category_str,
                address=shop_address,
                state=state,
                location=location,
                opening_time=opening_time,
                closing_time=closing_time,
                map_url=map_url
            )
            db.session.add(new_salon)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('owner.login'))
        except Exception as e:
            db.session.rollback()
            # Log the technical error but show a clean message to the user
            print(f"Registration Error: {str(e)}")
            flash('Registration failed. Please ensure all details are correct.', 'danger')
            
    return render_template('owner/register.html')

@owner_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        owner = Owner.query.filter_by(email=email, phone=phone).first()
        if owner:
            return redirect(url_for('owner.reset_password', owner_id=owner.id))
        flash('No account found with these details.', 'danger')
    return render_template('owner/forgot_password.html')

@owner_bp.route('/reset-password/<int:owner_id>', methods=['GET', 'POST'])
def reset_password(owner_id):
    owner = Owner.query.get_or_404(owner_id)
    if request.method == 'POST':
        new_password = request.form.get('password')
        owner.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password reset successful! Please login.', 'success')
        return redirect(url_for('owner.login'))
    return render_template('owner/reset_password.html', owner=owner)

from datetime import datetime, timedelta
from sqlalchemy import func

@owner_bp.route('/dashboard')
@login_required
def dashboard():
    # Ensure current_user is an owner
    if not isinstance(current_user, Owner):
        return redirect(url_for('owner.login'))
        
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if not salon:
        return "Please register a salon first." 
        
    stats = get_salon_stats(salon)
    bookings_list = Booking.query.filter_by(salon_id=salon.id).all()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 2. 7-Day Revenue Trend (Owner's Share)
    revenue_trend = []
    days_short = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        day_total = 0.0
        for b in bookings_list:
            if b.status == 'completed' and b.service and b.slot_time.date() == target_date.date():
                if b.commission_applied:
                    day_total += b.owner_share
                elif b.worker and b.worker.is_owner:
                    day_total += b.service.price
                else:
                    day_total += (b.service.price * 0.5)
        
        revenue_trend.append({
            'day': days_short[target_date.weekday()],
            'amount': round(day_total, 2)
        })

    # 3. Top Popular Services
    from collections import Counter
    service_counts = Counter([b.service.name for b in bookings_list if b.service])
    top_services = [{'name': name, 'count': count} for name, count in service_counts.most_common(4)]

    # 4. Filtered lists for the UI
    recent_bookings = sorted([b for b in bookings_list], key=lambda x: x.slot_time, reverse=True)[:5]
    workers = Worker.query.filter_by(salon_id=salon.id).all()

    # 5. Today's Cash Collection by Worker
    cash_data = []
    for w in workers:
        w_cash = sum(float(b.service.price) for b in bookings_list if b.worker_id == w.id 
                     and b.status == 'completed' and b.payment_method == 'Cash' 
                     and b.slot_time.date() == today.date() and b.service)
        if w_cash > 0:
            cash_data.append({'name': w.name, 'amount': w_cash, 'is_owner': w.is_owner})
    
    return render_template('owner/dashboard.html', 
                           stats=stats, 
                           revenue_trend=revenue_trend,
                           top_services=top_services,
                           appointments=recent_bookings, 
                           workers=workers,
                           today_cash_data=cash_data,
                           shop=salon,
                           active_page='dashboard')

@owner_bp.route('/bookings')
@login_required
def bookings():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if not salon:
        flash('Please register a salon first.', 'warning')
        return redirect(url_for('owner.dashboard'))
    appointments = Booking.query.filter_by(salon_id=salon.id).order_by(Booking.slot_time.desc()).all()
    return render_template('owner/bookings.html', 
                           appointments=appointments,
                           shop=salon,
                           active_page='bookings')

@owner_bp.route('/bookings/<int:id>/accept', methods=['POST'])
@login_required
def accept_booking(id):
    booking = Booking.query.get_or_404(id)
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if booking.salon_id != salon.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('owner.bookings'))
        
    import random, string
    otp = ''.join(random.choices(string.digits, k=6))
    booking.status = 'accepted'
    booking.otp = otp
    
    # Create notification for user
    from models import Notification
    notif = Notification(
        user_id=booking.user_id,
        title="Booking Confirmed! ✅",
        message=f"Your booking for {booking.service.name} at {salon.name} has been accepted. Show OTP {otp} at the salon.",
        type='booking'
    )
    db.session.add(notif)
    
    db.session.commit()
    flash(f'Booking accepted! The customer has received their OTP to start the service.', 'success')
    return redirect(url_for('owner.bookings'))

@owner_bp.route('/bookings/<int:id>/reject', methods=['POST'])
@login_required
def reject_booking(id):
    booking = Booking.query.get_or_404(id)
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if booking.salon_id != salon.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('owner.bookings'))
        
    booking.status = 'rejected'
    db.session.commit()
    flash('Booking has been rejected.', 'danger')
    return redirect(url_for('owner.bookings'))

@owner_bp.route('/bookings/<int:id>/verify-otp', methods=['POST'])
@login_required
def verify_otp(id):
    booking = Booking.query.get_or_404(id)
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if booking.salon_id != salon.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('owner.bookings'))
        
    otp = request.form.get('otp')
    pay_method = request.form.get('payment_method', 'Cash') # Default to Cash if not provided
    if booking.otp == otp:
        booking.status = 'completed'
        booking.payment_method = pay_method
        booking.payment_status = 'Paid'
        
        # Calculate revenue split
        if booking.service:
            total_price = float(booking.service.price)
            worker_amt = 0.0
            
            # If a worker is assigned
            if booking.worker:
                # Case 1: The worker IS the owner (100% to owner)
                if booking.worker.is_owner:
                    worker_amt = 0.0
                # Case 2: Worker is on Salary (usually 0% commission unless bonus)
                elif booking.worker.payment_type == 'salary':
                    worker_amt = 0.0
                # Case 3: Worker is on Commission (standard split)
                else:
                    rate = booking.worker.commission_rate or 50.0
                    worker_amt = (rate / 100.0) * total_price
                
                booking.worker_share = worker_amt
                booking.worker.total_earnings = (booking.worker.total_earnings or 0.0) + worker_amt
                booking.worker.current_balance = (booking.worker.current_balance or 0.0) + worker_amt
            
            booking.owner_share = total_price - worker_amt
            booking.commission_applied = True
        
        db.session.commit()
        flash('OTP verified! Booking marked as completed. 🎉', 'success')
    else:
        flash('Invalid OTP. Please try again.', 'danger')
    return redirect(url_for('owner.bookings'))

@owner_bp.route('/services', methods=['GET', 'POST'])
@login_required
def manage_services():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        duration = request.form.get('duration')
        description = request.form.get('description')
        
        # Use the provided URL or fall back to default
        image_url = request.form.get('image_url') or "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&q=80&w=400"
        
        new_service = Service(
            salon_id=salon.id,
            name=name,
            price=float(price),
            duration=int(duration) if duration else 30,
            description=description,
            image_url=image_url
        )
        db.session.add(new_service)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('owner.manage_services'))

    services = Service.query.filter_by(salon_id=salon.id).all()
    return render_template('owner/services.html', services=services, shop=salon, active_page='services')

@owner_bp.route('/services/delete/<int:id>', methods=['POST'])
@login_required
def delete_service(id):
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    service = Service.query.get_or_404(id)
    
    # Security check: ensure the service belongs to the owner's salon
    if service.salon_id != salon.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('owner.manage_services'))
        
    try:
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error: Cannot delete this service because it is currently linked to existing bookings.', 'danger')
        print(f"Delete Service Error: {str(e)}")
        
    return redirect(url_for('owner.manage_services'))

@owner_bp.route('/services/bulk_add', methods=['POST'])
@login_required
def bulk_add_services():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if not salon:
        return redirect(url_for('owner.dashboard'))
        
    selected_services = request.form.getlist('selected_services')
    
    added_count = 0
    for svc_name in selected_services:
        price = request.form.get(f"price_{svc_name}")
        duration = request.form.get(f"duration_{svc_name}")
        
        if price and duration:
            img = "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&q=80&w=400"
            if 'Hair' in svc_name or 'Cut' in svc_name or 'Shave' in svc_name:
                img = "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=500&q=80"
            elif 'Makeup' in svc_name or 'Wax' in svc_name or 'Bleach' in svc_name or 'Whitening' in svc_name:
                img = "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=500&q=80"
            elif 'Massage' in svc_name or 'Spa' in svc_name or 'Scrub' in svc_name:
                img = "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=500&q=80"
            elif 'Nail' in svc_name or 'Manicure' in svc_name or 'Pedicure' in svc_name:
                img = "https://images.unsplash.com/photo-1522337660859-02fbefca4702?w=500&q=80"
            elif 'Tattoo' in svc_name:
                img = "https://images.unsplash.com/photo-1598371839696-5c5bb00bdc28?w=500&q=80"
                
            new_service = Service(
                salon_id=salon.id,
                name=svc_name,
                price=float(price),
                duration=int(duration),
                description=f"Professional {svc_name} treatment.",
                image_url=img
            )
            db.session.add(new_service)
            added_count += 1
            
    db.session.commit()
    flash(f'{added_count} services added successfully via Bulk Setup!', 'success')
    return redirect(url_for('owner.manage_services'))

@owner_bp.route('/workers', methods=['GET', 'POST'])
@login_required
def manage_workers():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        experience = request.form.get('experience')
        skills = request.form.get('skills')
        commission_rate = request.form.get('commission_rate', 50.0) # Default to 50%
        payment_type = request.form.get('payment_type', 'commission')
        salary_amount = request.form.get('salary_amount', 0.0)
        selected_services = request.form.getlist('services_list')
        assigned_services = ", ".join(selected_services)
        
        # Check if worker phone already exists
        if Worker.query.filter_by(phone=phone).first():
            flash('Worker with this phone number already exists', 'danger')
            return redirect(url_for('owner.manage_workers'))
            
        new_worker = Worker(
            salon_id=salon.id,
            name=name,
            phone=phone,
            experience=int(experience),
            skill=skills,
            payment_type=payment_type,
            salary_amount=float(salary_amount) if salary_amount else 0.0,
            commission_rate=float(commission_rate) if commission_rate else 50.0,
            is_approved=True, # Owners manual additions are approved by default
            password=generate_password_hash("worker123") # Default password
        )
        db.session.add(new_worker)
        db.session.commit()
        flash('New expert added successfully!', 'success')
        return redirect(url_for('owner.manage_workers'))

    approved_workers = Worker.query.filter_by(salon_id=salon.id, is_approved=True).all()
    pending_workers = Worker.query.filter_by(salon_id=salon.id, is_approved=False).all()
    services = Service.query.filter_by(salon_id=salon.id).all()
    
    # Calculate daily stats
    today_start = datetime.combine(datetime.today(), time.min)
    today_end = datetime.combine(datetime.today(), time.max)
    
    worker_stats = []
    total_working_today = 0
    
    for worker in approved_workers:
        today_bookings = Booking.query.filter(
            Booking.worker_id == worker.id,
            Booking.slot_time >= today_start,
            Booking.slot_time <= today_end
        ).all()
        
        completed_bookings = [b for b in today_bookings if b.status == 'completed']
        if len(today_bookings) > 0 or worker.status == 'online':
            total_working_today += 1
            
        # Revenue is the owner's net share
        revenue = sum(b.owner_share if b.commission_applied else (b.service.price * 0.5) 
                      for b in completed_bookings if b.service)
        
        # Total shop intake from this worker
        total_intake = sum(b.service.price for b in completed_bookings if b.service)
        
        service_breakdown = {}
        for b in completed_bookings:
            if b.service:
                if b.service.name not in service_breakdown:
                    service_breakdown[b.service.name] = {'count': 0, 'amount': 0.0}
                service_breakdown[b.service.name]['count'] += 1
                service_breakdown[b.service.name]['amount'] += b.service.price
        
        worker_stats.append({
            'worker': worker,
            'total_today': len(today_bookings),
            'completed': len(completed_bookings),
            'revenue': revenue,
            'total_intake': total_intake,
            'service_breakdown': service_breakdown
        })
        
    is_owner_worker = Worker.query.filter_by(phone=current_user.phone).first() is not None

    return render_template('owner/workers.html', 
                           workers=approved_workers, 
                           pending_workers=pending_workers, 
                           services=services, 
                           worker_stats=worker_stats,
                           total_working_today=total_working_today,
                           is_owner_worker=is_owner_worker,
                           salon=salon,
                           active_page='workers')

@owner_bp.route('/workers/add_self', methods=['POST'])
@login_required
def add_self_worker():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if Worker.query.filter_by(phone=current_user.phone).first():
        flash('You are already registered as a worker.', 'warning')
        return redirect(url_for('owner.manage_workers'))
    
    # Auto-detect skill from salon category (matches register.html values)
    category_skill_map = {
        'barber shop':    'Barber',
        'beauty parlor':  'Beauty Parlour',
        'beauty parlour': 'Beauty Parlour',
        'spa & wellness': 'Spa Therapist',
        'spa':            'Spa Therapist',
        'tattoo studio':  'Tattoo Artist',
        'tattoo':         'Tattoo Artist',
        'nail salon':     'Nail Artist',
        'makeup':         'Makeup Artist',
        'hair accessories': 'Stylist',
        'hair salon':     'Hair Stylist',
        'salon':          'All Services',
    }

    cat = (salon.category or 'salon').strip().lower()
    # Try longest key match first so "barber shop" beats "barber"
    auto_skill = 'All Services'
    for key in sorted(category_skill_map, key=len, reverse=True):
        if key in cat:
            auto_skill = category_skill_map[key]
            break
    
    new_worker = Worker(
        salon_id=salon.id,
        name=f"{current_user.name} (Owner)",
        phone=current_user.phone,
        experience=5,
        skill=auto_skill,
        is_approved=True,
        is_owner=True, # Explicitly mark as owner-worker
        payment_type='salary', # Owners don't pay themselves commission usually
        password=current_user.password,
        image_url=current_user.profile_image or "https://i.pravatar.cc/300"
    )
    db.session.add(new_worker)
    db.session.commit()
    flash(f'✅ You joined as a {auto_skill} worker (based on your salon type). Login to the Worker App with your phone & password.', 'success')
    return redirect(url_for('owner.manage_workers'))


@owner_bp.route('/workers/delete/<int:id>', methods=['POST'])
@login_required
def delete_worker(id):
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    worker = Worker.query.get_or_404(id)
    
    if worker.salon_id != salon.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('owner.manage_workers'))
    
    try:
        # Step 1: Unlink all bookings referencing this worker
        # (worker_id is now nullable so this is safe)
        worker_bookings = Booking.query.filter_by(worker_id=id).all()
        for b in worker_bookings:
            b.worker_id = None  # unlink; booking record remains for history
            if b.status in ('pending', 'accepted'):
                b.status = 'unassigned'  # mark as needing reassignment
        db.session.flush()
        
        # Step 2: Now safely delete the worker
        db.session.delete(worker)
        db.session.commit()
        flash(f'Worker removed successfully! Their {len(worker_bookings)} booking(s) have been marked as unassigned.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Delete Worker Error: {str(e)}")
        flash('Error removing worker. Please try again.', 'danger')
        
    return redirect(url_for('owner.manage_workers'))

@owner_bp.route('/workers/approve/<int:worker_id>', methods=['POST'])
@login_required
def approve_worker(worker_id):
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    worker = Worker.query.filter_by(id=worker_id, salon_id=salon.id).first()
    
    if worker:
        worker.is_approved = True
        db.session.commit()
        flash(f'Expert {worker.name} approved successfully!', 'success')
    else:
        flash('Worker not found or unauthorized', 'danger')
        
    return redirect(request.referrer or url_for('owner.manage_workers'))

@owner_bp.route('/workers/reject/<int:worker_id>', methods=['POST'])
@login_required
def reject_worker(worker_id):
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    worker = Worker.query.filter_by(id=worker_id, salon_id=salon.id).first()
    
    if worker:
        db.session.delete(worker)
        db.session.commit()
        flash(f'Request from {worker.name} has been rejected.', 'info')
    else:
        flash('Worker not found or unauthorized', 'danger')
        
    return redirect(request.referrer or url_for('owner.manage_workers'))

@owner_bp.route('/workers/payout/<int:worker_id>', methods=['POST'])
@login_required
def payout_worker(worker_id):
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    worker = Worker.query.filter_by(id=worker_id, salon_id=salon.id).first()
    
    if worker:
        payout_amount = worker.current_balance or 0.0
        worker.current_balance = 0.0
        db.session.commit()
        flash(f'Successfully recorded ₹{int(payout_amount)} payout for {worker.name}! 💸', 'success')
    else:
        flash('Worker not found or unauthorized', 'danger')
        
    return redirect(url_for('owner.manage_workers'))




@owner_bp.route('/profile')
@login_required
def profile():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if not salon:
        flash('Please register a salon first.', 'warning')
        return redirect(url_for('owner.dashboard'))
    
    stats = get_salon_stats(salon)
    return render_template('owner/profile.html', shop=salon, stats=stats, active_page='profile')

@owner_bp.route('/notifications')
@login_required
def notifications():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    # Fetch recent bookings as notifications for now
    notifications_list = Booking.query.filter_by(salon_id=salon.id).order_by(Booking.slot_time.desc()).limit(15).all()
    # Fetch pending workers
    pending_workers = Worker.query.filter_by(salon_id=salon.id, is_approved=False).all()
    return render_template('owner/notifications.html', notifications=notifications_list, pending_workers=pending_workers, active_page='notifications')

@owner_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    
    if request.method == 'POST':
        # 1. Update Owner Profile
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        
        # Determine if a file was uploaded or a URL was pasted
        file = request.files.get('profile_image_file')
        if file and file.filename != '':
            from werkzeug.utils import secure_filename
            filename = secure_filename(f"user_{current_user.id}_{file.filename}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'owner_profiles')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            current_user.profile_image = url_for('static', filename=f'uploads/owner_profiles/{filename}')
        elif request.form.get('profile_image'):
            # Fallback to URL if provided
            current_user.profile_image = request.form.get('profile_image')
        
        new_password = request.form.get('password')
        if new_password:
            current_user.password = generate_password_hash(new_password)
            
        # 2. Update Shop Details (if linked)
        if salon:
            salon.name = request.form.get('shop_name')
            salon.category = request.form.get('shop_category') # NEW: Allow category change
            salon.address = request.form.get('shop_address')
            salon.state = request.form.get('state')
            salon.location = request.form.get('city') # the city
            salon.opening_time = request.form.get('opening_time')
            salon.closing_time = request.form.get('closing_time')
            salon.map_url = request.form.get('map_url')
            salon.upi_id = request.form.get('upi_id')
            
            # Auto-generate QR Code if UPI ID is present
            if salon.upi_id:
                # Format: upi://pay?pa=UPI_ID&pn=SALON_NAME&cu=INR
                import urllib.parse
                safe_name = urllib.parse.quote(salon.name)
                upi_data = f"upi://pay?pa={salon.upi_id}&pn={safe_name}&cu=INR"
                safe_upi = urllib.parse.quote(upi_data)
                salon.qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={safe_upi}"
            
            salon.is_active = True if request.form.get('is_active') == 'on' else False
            
            # Save Excellence Categories
            excellence_list = request.form.getlist('excellence_list')
            salon.excellence_categories = ",".join(excellence_list) if excellence_list else None
            
            # Shop Logo Upload
            logo_file = request.files.get('shop_logo_file')
            if logo_file and logo_file.filename != '':
                from werkzeug.utils import secure_filename
                logo_filename = secure_filename(f"salon_logo_{salon.id}_{logo_file.filename}")
                logo_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'shop_logos')
                os.makedirs(logo_folder, exist_ok=True)
                logo_path = os.path.join(logo_folder, logo_filename)
                logo_file.save(logo_path)
                salon.logo_url = url_for('static', filename=f'uploads/shop_logos/{logo_filename}')
            
            # Shop Gallery Photos Upload
            gallery_files = request.files.getlist('shop_photos_list')
            new_photo_urls = []
            for g_file in gallery_files:
                if g_file and g_file.filename != '':
                    from werkzeug.utils import secure_filename
                    g_filename = secure_filename(f"salon_gal_{salon.id}_{g_file.filename}")
                    gallery_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'shop_gallery')
                    os.makedirs(gallery_folder, exist_ok=True)
                    g_path = os.path.join(gallery_folder, g_filename)
                    g_file.save(g_path)
                    new_photo_urls.append(url_for('static', filename=f'uploads/shop_gallery/{g_filename}'))
            
            if new_photo_urls:
                # Append to existing photos or set new ones
                current_photos = salon.shop_photos.split(',') if salon.shop_photos else []
                current_photos.extend(new_photo_urls)
                salon.shop_photos = ','.join(current_photos)
            
        db.session.commit()
        flash('Account and Shop settings updated successfully!', 'success')
        return redirect(url_for('owner.settings'))
        
    return render_template('owner/settings.html', shop=salon, active_page='settings')

@owner_bp.route('/toggle_status', methods=['POST'])
@login_required
def toggle_status():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if not salon:
        return jsonify({'success': False, 'message': 'Salon not found'}), 404
        
    salon.is_active = not salon.is_active
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'is_active': salon.is_active,
        'message': 'Shop status updated!'
    })

@owner_bp.route('/earnings')
@login_required
def earnings():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if not salon:
        flash('Please register a salon first.', 'warning')
        return redirect(url_for('owner.dashboard'))
    
    all_bookings = Booking.query.filter_by(salon_id=salon.id).order_by(Booking.slot_time.desc()).all()
    completed = [b for b in all_bookings if b.status == 'completed']
    
    total_revenue = sum(b.service.price for b in completed if b.service)
    owner_total = sum(b.owner_share if b.commission_applied else (b.service.price * 0.5) for b in completed if b.service)
    worker_payouts = total_revenue - owner_total

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue = sum(b.service.price for b in completed if b.service and b.slot_time >= today)
    today_owner = sum(b.owner_share if b.commission_applied else (b.service.price * 0.5) for b in completed if b.service and b.slot_time >= today)
    
    return render_template('owner/earnings.html',
                           shop=salon,
                           total_revenue=total_revenue,
                           owner_income=owner_total,
                           worker_payouts=worker_payouts,
                           today_revenue=today_revenue,
                           today_owner=today_owner,
                           completed_bookings=completed,
                           all_bookings=all_bookings,
                           active_page='earnings')

@owner_bp.route('/offers', methods=['GET', 'POST'])
@login_required
def manage_offers():
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if not salon:
        flash('Please register a salon first.', 'warning')
        return redirect(url_for('owner.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        discount_tag = request.form.get('discount_tag')
        
        offer = Offer(
            salon_id=salon.id,
            title=title,
            description=description,
            discount_tag=discount_tag,
            is_active=True
        )

        # Handle Offer Image
        file = request.files.get('offer_image')
        if file and file.filename != '':
            from werkzeug.utils import secure_filename
            filename = secure_filename(f"offer_{salon.id}_{file.filename}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'offers')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            offer.image_url = url_for('static', filename=f'uploads/offers/{filename}')
        
        db.session.add(offer)
        
        # Notify all users about the new offer
        from models import User, Notification
        users = User.query.all()
        for u in users:
            notif = Notification(
                user_id=u.id,
                title=f"New Offer at {salon.name}! 🎁",
                message=f"{offer.title}: {offer.description or 'Check it out now!'}",
                type='offer'
            )
            db.session.add(notif)
            
        db.session.commit()
        flash('New offer added successfully! 🎁', 'success')
        return redirect(url_for('owner.manage_offers'))

    offers = Offer.query.filter_by(salon_id=salon.id).order_by(Offer.created_at.desc()).all()
    return render_template('owner/offers.html', salon=salon, offers=offers, active_page='offers')

@owner_bp.route('/offers/delete/<int:id>', methods=['POST'])
@login_required
def delete_offer(id):
    offer = Offer.query.get_or_404(id)
    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if offer.salon_id != salon.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('owner.manage_offers'))
    
    db.session.delete(offer)
    db.session.commit()
    flash('Offer removed.', 'success')
    return redirect(url_for('owner.manage_offers'))

@owner_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('owner.login'))
