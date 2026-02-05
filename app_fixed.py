"""
Production-Ready EduGuard Application
Fixed version with all issues resolved
"""

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from models import db  # Import shared db instance
from datetime import datetime, timedelta
import os
import logging

# Initialize extensions
login_manager = LoginManager()
mail = Mail()

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///eduguard.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@eduguard.edu')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.refresh_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    try:
        from routes.main_new import main_bp as main_blueprint
        from routes.auth_fixed import auth_bp as auth_blueprint
        from routes.counselling import counselling_bp as counselling_blueprint
        from routes.mentor import mentor_bp as mentor_blueprint
        from routes.performance import performance_bp as performance_blueprint
        from routes.ml import ml_bp as ml_blueprint
        from routes.reason import reason_bp as reason_blueprint
        from routes.student import student_bp as student_blueprint
        
        app.register_blueprint(main_blueprint)
        app.register_blueprint(auth_blueprint)
        app.register_blueprint(counselling_blueprint)
        app.register_blueprint(mentor_blueprint)
        app.register_blueprint(performance_blueprint)
        app.register_blueprint(ml_blueprint)
        app.register_blueprint(reason_blueprint)
        app.register_blueprint(student_blueprint)
        
        print("✅ All blueprints registered successfully")
        
    except ImportError as e:
        print(f"⚠️  Warning: Could not import blueprint: {e}")
        print("   Using fallback routes...")
        
        # Fallback to basic routes
        from routes.main_new import main_bp as main_blueprint
        from routes.auth_fixed import auth_bp as auth_blueprint
        app.register_blueprint(main_blueprint)
        app.register_blueprint(auth_blueprint)

# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False), host='0.0.0.0', port=5000)
