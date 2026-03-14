from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import User, Worker, Owner, OTPVerification
from utils.sms_service import SMSService
import random
from extensions import db, limiter

auth_bp = Blueprint('auth', __name__)

# Temporary store for login/reg OTPs (In production, use Redis or a DB table)
otp_store = {}

@auth_bp.route('/send-otp', methods=['POST'])
@limiter.limit("3 per hour", error_message="Too many OTP requests. Please try again later.")
def send_otp():
    data = request.json
    phone = data.get('phone')
    if not phone:
        return jsonify({"message": "Phone number required", "status": "error"}), 400
    
    otp_record = OTPVerification(phone=phone, purpose='login')
    db.session.add(otp_record)
    db.session.commit()
    
    success, msg = SMSService.send_otp(phone, otp_record.otp, "Saloon Essy")
    if success:
        return jsonify({"message": "OTP sent successfully", "status": "success"})
    return jsonify({"message": f"Failed to send OTP: {msg}", "status": "error"}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
@limiter.limit("5 per hour", error_message="Too many failed attempts. Please try again later.")
def verify_otp_login():
    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')
    
    if OTPVerification.verify_otp(phone, otp, purpose='login'):
        user = User.query.filter_by(phone=phone).first()
        if user:
            if not user.is_active:
                return jsonify({"message": "Your account has been suspended. Please contact support.", "status": "suspended"}), 403
            return jsonify({
                "message": "Login successful",
                "status": "success",
                "user_id": user.id,
                "role": "user"
            })
        else:
            # First time user verified via mobile
            return jsonify({
                "message": "Phone verified, please complete registration",
                "status": "new_user",
                "phone": phone
            })
            
    return jsonify({"message": "Invalid or expired OTP", "status": "error"}), 401

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    role = data.get('role') # 'user', 'worker', 'owner'

    if role == 'user':
        user = User.query.filter_by(phone=phone).first()
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                return jsonify({"message": "Your account has been suspended.", "status": "suspended"}), 403
            return jsonify({
                "message": "User login successful",
                "status": "success",
                "user_id": user.id,
                "role": "user"
            })
    elif role == 'worker':
        worker = Worker.query.filter_by(phone=phone).first()
        if worker and check_password_hash(worker.password, password):
            if not worker.is_active:
                return jsonify({"message": "Your account is deactivated.", "status": "suspended"}), 403
            if not worker.is_approved:
                return jsonify({
                    "message": "Your account is pending approval by the shop owner.",
                    "status": "pending",
                    "role": "worker"
                }), 403
            return jsonify({
                "message": "Worker login successful",
                "status": "success",
                "worker_id": worker.id,
                "role": "worker"
            })
    elif role == 'owner':
        owner = Owner.query.filter_by(phone=phone).first()
        if owner and check_password_hash(owner.password, password):
            if not owner.is_active:
                return jsonify({"message": "Your owner account is suspended.", "status": "suspended"}), 403
            return jsonify({
                "message": "Owner login successful",
                "status": "success",
                "owner_id": owner.id,
                "role": "owner"
            })

    return jsonify({"message": "Invalid credentials or role", "status": "error"}), 401
