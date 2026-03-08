from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import User, Worker, Owner

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    role = data.get('role') # 'user', 'worker', 'owner'

    if role == 'user':
        user = User.query.filter_by(phone=phone).first()
        if user and check_password_hash(user.password, password):
            return jsonify({
                "message": "User login successful",
                "status": "success",
                "user_id": user.id,
                "role": "user"
            })
    elif role == 'worker':
        worker = Worker.query.filter_by(phone=phone).first()
        if worker and check_password_hash(worker.password, password):
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
            return jsonify({
                "message": "Owner login successful",
                "status": "success",
                "owner_id": owner.id,
                "role": "owner"
            })

    return jsonify({"message": "Invalid credentials or role", "status": "error"}), 401
