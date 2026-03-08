from flask import Flask, jsonify, render_template
from flask_cors import CORS
from extensions import db, login_manager
from config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.jinja_env.add_extension('jinja2.ext.do')

    # Enable CORS for cross-origin requests from mobile apps
    CORS(app)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message_category = 'info'

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, redirect, url_for, flash
        if request.path.startswith('/worker'):
            flash('Worker login required.', 'warning')
            return redirect(url_for('worker_panel.login'))
        elif request.path.startswith('/owner'):
            flash('Access reserved for Salon Owners. Please login.', 'info')
            return redirect(url_for('owner.login'))
        else:
            flash('Please login to continue.', 'info')
            return redirect(url_for('user_portal.login'))

    # Unified user loader for all 3 roles
    from models import User, Worker, Owner
    
    @login_manager.user_loader
    def load_user(user_id):
        # We use a prefixed id to handle multiple tables (e.g., "owner:1")
        if ":" in user_id:
            role, id = user_id.split(":")
            if role == "user": return User.query.get(int(id))
            if role == "worker": return Worker.query.get(int(id))
            if role == "owner": return Owner.query.get(int(id))
        return None

    # Register Blueprints
    from routes.user_routes import user_bp
    from routes.worker_routes import worker_bp
    from routes.owner_routes import owner_bp
    from routes.auth_routes import auth_bp
    from routes.worker_panel_routes import worker_panel_bp
    from routes.user_portal_routes import user_portal_bp

    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(worker_bp, url_prefix='/worker')
    app.register_blueprint(owner_bp, url_prefix='/owner')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(worker_panel_bp)
    app.register_blueprint(user_portal_bp)

    @app.context_processor
    def utility_processor():
        from flask_login import current_user
        from models import Worker, Salon, Owner
        pending_count = 0
        if current_user.is_authenticated and isinstance(current_user, Owner):
            salon = Salon.query.filter_by(owner_id=current_user.id).first()
            if salon:
                pending_count = Worker.query.filter_by(salon_id=salon.id, is_approved=False).count()
        return dict(pending_staff_count=pending_count)

    @app.route('/')
    def home():
        from flask_login import current_user
        return render_template('index.html', current_user=current_user)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Ensure all models are registered and tables created
        from models import User, Worker, Owner, Salon, Service, Booking
        db.create_all()
    
    # Run server - accesible in network via host='0.0.0.0'
    app.run(host='0.0.0.0', port=5000, debug=True)
