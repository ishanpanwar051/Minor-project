"""
Enhanced App Factory for EduGuard System
Production-ready Flask application factory with security and monitoring
"""

from flask import Flask
from config_enhanced import Config
from models import db, User
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_cors import CORS
from flask_talisman import Talisman
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import os

# Configure logging
def setup_logging(app):
    """Setup application logging"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create file handler
    file_handler = RotatingFileHandler(
        filename=Config.LOG_FILE,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=5,
        encoding='utf-8'
    )
    
    # Configure logging level
    level = getattr(logging, Config.LOG_LEVEL, logging.INFO)
    file_handler.setLevel(level)
    
    # Configure formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger = logging.getLogger(Config.APP_NAME)
    logger.addHandler(file_handler)
    
    # Set logging level
    logger.setLevel(level)
    
    # Configure Flask logger
    app.logger.addHandler(logger)
    
    return logger

def create_app():
    """Create and configure Flask application with enhanced security"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    # Initialize Flask-CORS for API
    if Config.CORS_ORIGINS and Config.CORS_METHODS:
        CORS(app, origins=Config.CORS_ORIGINS, methods=Config.CORS_SETHODS)
    
    # Initialize Flask-Talisman for security headers
    if Config.is_production():
        talisman = Talisman(
            frame_options={
                'force-https': True,
                'strict-transport-security': True,
                'strict-dynamic': True,
                'session-cookie-secure': Config.SESSION_COOKIE_SECURE,
                'session-cookie-httponly': Config.SESSION_COOKIE_HTTPONLY,
                'session-cookie-samesite': Config.SESSION_COOKIE_SAMESITE
            }
        )
        talisman.init_app(app)
    
    # Initialize Flask-Limiter for rate limiting
    if Config.RATELIMIT_ENABLED:
        limiter = Limiter(
            key_func=lambda: request.form.get('api_key'),
            default=Config.RATELIMIT_DEFAULT,
            per_method=Config.RATELIMIT_WINDOW,
            storage_uri='memory://',
            headers=Config.SECURITY_HEADERS
        )
        limiter.init_app(app)
    
    # Setup logging
    logger = setup_logging(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register Blueprints
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
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")
    
    return app

def get_app():
    """Get configured Flask application"""
    return create_app()
