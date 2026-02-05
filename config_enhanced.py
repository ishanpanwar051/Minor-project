"""
Enhanced Configuration for EduGuard System
Environment variables, security settings, and production configuration
"""

import os
from datetime import timedelta

class Config:
    """Enhanced configuration class for EduGuard"""
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///eduguard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@eduguard.edu')
    
    # Security Configuration
    SECURITY_PASSWORD_HASH = os.environ.get('SECURITY_PASSWORD_HASH', 'pbkdf2_sha256:hashed_password')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'secure_salt_for_hashing')
    
    # Session Configuration
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))  # 1 hour
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'False').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = '100 per hour'
    RATELIMIT_WINDOW = 3600  # 1 hour
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.gif']
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.environ.get('LOG_FILE', 'eduguard.log')
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').lower().split(',')
    CORS_METHODS = os.environ.get('CORS_METHODS', 'GET, POST, PUT, DELETE, OPTIONS').lower().split(',')
    
    # Cache Configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))  # 5 minutes
    
    # Production Settings
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    PRODUCTION = os.environ.get('PRODUCTION', 'False').lower() == 'true'
    
    # Application Settings
    APP_NAME = os.environ.get('APP_NAME', 'EduGuard')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
    }
    
    @staticmethod
    def init_app(app):
        """Initialize Flask app with enhanced configuration"""
        # Configure session security
        app.config.update(
            SESSION_COOKIE_SECURE=Config.SESSION_COOKIE_SECURE,
            SESSION_COOKIE_HTTPONLY=Config.SESSION_COOKIE_HTTPONLY,
            SESSION_COOKIE_SAMESITE=Config.SESSION_COOKIE_SAMESITE,
            PERMANENT_SESSION_LIFETIME=Config.SESSION_TIMEOUT
        )
        
        # Configure security headers
        app.config.update(Config.SECURITY_HEADERS)
        
        # Configure CORS if enabled
        if Config.CORS_ORIGINS and Config.CORS_METHODS:
            from flask_cors import CORS
            cors = CORS(app, origins=Config.CORS_ORIGINS, methods=Config.CORS_METHODS)
            app.config['CORS_HEADERS'] = cors.headers
        
        # Configure rate limiting
        if Config.RATELIMIT_ENABLED:
            from flask_limiter import Limiter
            limiter = Limiter(
                key_func=lambda: lambda: request.form.get('api_key'),
                default=Config.RATELIMIT_DEFAULT,
                per_method=Config.RATELIMIT_WINDOW,
                storage_uri='memory://',
                headers=Config.SECURITY_HEADERS
            )
            limiter.init_app(app)
        
        return app
    
    @staticmethod
    def get_env_var(key, default=''):
        """Get environment variable with fallback"""
        return os.environ.get(key, default)
    
    @staticmethod
    def is_production():
        """Check if running in production"""
        return Config.PRODUCTION.lower() == 'true'
    
    @staticmethod
    def is_development():
        """Check if running in development"""
        return Config.DEBUG.lower() == 'true' or not Config.PRODUCTION
