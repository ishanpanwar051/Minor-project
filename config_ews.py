"""
Enhanced Configuration for Early Warning System (EWS)
Supports PostgreSQL, Redis, Celery, and production deployment
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    DEBUG = False
    TESTING = False
    
    # Database Configuration - PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:password@localhost:5432/eduguard_ews'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'pool_pre_ping': True,
        'max_overflow': 30
    }
    
    # Security Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    RATELIMIT_DEFAULT = '200 per day, 50 per hour'
    RATELIMIT_HEADERS_ENABLED = True
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_MAX_EMAILS = int(os.environ.get('MAIL_MAX_EMAILS') or 10)
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/2'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx', 'doc', 'docx'}
    
    # Application Configuration
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE') or 20)
    PAGINATION_MAX_PER_PAGE = 100
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/eduguard_ews.log'
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES') or 10 * 1024 * 1024)  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT') or 5)
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
    }
    
    # API Configuration
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    # Cache Configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'redis'
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT') or 300)
    
    # ML Configuration
    ML_MODEL_PATH = os.environ.get('ML_MODEL_PATH') or 'model/model.pkl'
    ML_SCALER_PATH = os.environ.get('ML_SCALER_PATH') or 'model/scaler.pkl'
    ML_RETRAIN_INTERVAL = int(os.environ.get('ML_RETRAIN_INTERVAL') or 7)  # days
    
    # Notification Configuration
    NOTIFICATION_ENABLED = os.environ.get('NOTIFICATION_ENABLED', 'True').lower() == 'true'
    SMS_ENABLED = os.environ.get('SMS_ENABLED', 'False').lower() == 'true'
    SMS_PROVIDER = os.environ.get('SMS_PROVIDER') or 'twilio'
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # Background Jobs Configuration
    BACKGROUND_TASKS_ENABLED = os.environ.get('BACKGROUND_TASKS_ENABLED', 'True').lower() == 'true'
    RISK_ASSESSMENT_INTERVAL = int(os.environ.get('RISK_ASSESSMENT_INTERVAL') or 24)  # hours
    ALERT_CHECK_INTERVAL = int(os.environ.get('ALERT_CHECK_INTERVAL') or 1)  # hours
    
    # Performance Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    
    # File Storage
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_S3_REGION = os.environ.get('AWS_S3_REGION') or 'us-east-1'
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configure logging
        file_handler = RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        app.logger.info('EduGuard EWS startup')
        
        # Initialize Sentry if DSN is provided
        if Config.SENTRY_DSN:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=Config.SENTRY_DSN,
                integrations=[FlaskIntegration()],
                traces_sample_rate=0.1,
                environment=os.environ.get('FLASK_ENV', 'production')
            )

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///eduguard_ews_dev.db'
    
    # Disable security headers for development
    SESSION_COOKIE_SECURE = False
    
    # Enable debug toolbar
    # FLASK_DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    # Disable email sending in development
    MAIL_SUPPRESS_SEND = True
    
    # More lenient rate limiting for development
    RATELIMIT_DEFAULT = '1000 per day, 100 per hour'
    
    # Disable background tasks in development
    BACKGROUND_TASKS_ENABLED = False
    
    # Shorter intervals for development
    RISK_ASSESSMENT_INTERVAL = 1  # hour
    ALERT_CHECK_INTERVAL = 10  # minutes

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable rate limiting for testing
    RATELIMIT_ENABLED = False
    
    # Disable email sending for testing
    MAIL_SUPPRESS_SEND = True
    
    # Disable background tasks for testing
    BACKGROUND_TASKS_ENABLED = False
    
    # Short session lifetime for testing
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)
    
    # Disable logging for tests
    LOG_LEVEL = 'WARNING'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/eduguard_ews'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Strict rate limiting for production
    RATELIMIT_DEFAULT = '100 per day, 25 per hour'
    
    # Enable email in production
    MAIL_SUPPRESS_SEND = False
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Enable background tasks in production
    BACKGROUND_TASKS_ENABLED = True
    
    # Longer intervals for production
    RISK_ASSESSMENT_INTERVAL = 24  # hours
    ALERT_CHECK_INTERVAL = 1  # hour
    
    # Production database pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'pool_pre_ping': True,
        'max_overflow': 30
    }

class StagingConfig(ProductionConfig):
    """Staging configuration"""
    DEBUG = True
    TESTING = False
    
    # Use staging database
    SQLALCHEMY_DATABASE_URI = os.environ.get('STAGING_DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/eduguard_ews_staging'
    
    # Staging-specific settings
    LOG_LEVEL = 'INFO'
    RATELIMIT_DEFAULT = '200 per day, 50 per hour'
    
    # Enable background tasks in staging
    BACKGROUND_TASKS_ENABLED = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    return config[os.getenv('FLASK_ENV', 'default')]
