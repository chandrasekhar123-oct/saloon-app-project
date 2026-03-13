from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_cors import CORS
from extensions import db, login_manager
from config import Config
import os

def create_admin_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.jinja_env.add_extension('jinja2.ext.do')

    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message_category = 'info'

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Admin login required.', 'warning')
        return redirect(url_for('admin.login'))

    # User loader that ONLY handles SuperAdmin
    from models import SuperAdmin
    
    @login_manager.user_loader
    def load_user(user_id):
        if ":" in user_id:
            role, id = user_id.split(":")
            if role == "admin": 
                return SuperAdmin.query.get(int(id))
        return None

    # Register ONLY Admin Blueprint
    from routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/')

    @app.route('/health')
    def health():
        return jsonify({"status": "Admin Panel Online"})

    return app

app = create_admin_app()

if __name__ == '__main__':
    # Run admin server on a different port (e.g., 5001)
    app.run(host='0.0.0.0', port=5001, debug=True)
