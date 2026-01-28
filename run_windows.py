from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
import logging
from datetime import datetime
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
mail = Mail()

def create_app(config_name='development'):
    """
    Application factory pattern for Windows development
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///eduguard_dev.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['WTF_CSRF_ENABLED'] = True
        app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT') or 587)
        app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
        app.config['SESSION_COOKIE_SECURE'] = False  # For development
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
        app.config['ITEMS_PER_PAGE'] = 20
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            from models_new import User
            return User.query.get(int(user_id))
        except:
            return None
    
    # Register blueprints
    try:
        from routes.auth import auth_bp
        from routes.main import main_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(main_bp)
    except ImportError as e:
        print(f"Warning: Could not import blueprints: {e}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return f"Page not found: {error}", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        try:
            db.session.rollback()
        except:
            pass
        return f"Internal server error: {error}", 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return f"Access forbidden: {error}", 403
    
    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/eduguard.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('EduGuard startup')
    
    # Create database tables
    with app.app_context():
        try:
            # Import models here to avoid circular imports
            from models_new import db as models_db
            models_db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
            # Try with original models as fallback
            try:
                from models import db as old_db
                old_db.create_all()
                print("Database tables created successfully with original models")
            except Exception as e2:
                print(f"Error with original models too: {e2}")
    
    return app

# Create app instance for development
app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
