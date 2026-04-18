#!/usr/bin/env python3
"""
Main Flask Application with Complete RBAC Integration
Production-ready EduGuard application with role-based access control
"""

from flask import Flask, render_template, request, session, redirect, url_for
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# ================================
# CONFIGURATION
# ================================

# Basic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///eduguard.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# CSRF protection
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# Pagination
app.config['ITEMS_PER_PAGE'] = 20

# File upload
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# ================================
# INITIALIZE EXTENSIONS
# ================================

# Database (use the shared models extension instance)
from models import db
db.init_app(app)

# CSRF Protection
csrf = CSRFProtect(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# ================================
# USER LOADER
# ================================

@login_manager.user_loader
def load_user(user_id):
    """
    Load user from database for Flask-Login
    """
    from models import User
    return User.query.get(int(user_id))

# ================================
# BLUEPRINT REGISTRATION
# ================================

# Import blueprints
from auth_routes import auth_bp
from admin_routes_rbac import admin_bp
from student_routes_rbac import student_bp
from rbac_system import handle_unauthorized_access, handle_forbidden_access

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)

# Legacy blueprint support (if needed)
try:
    from routes import main_bp
    from support_routes import support_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(support_bp)
except ImportError:
    print("Warning: Legacy blueprints not found. Using only RBAC routes.")

# ================================
# ERROR HANDLERS
# ================================

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    if request.is_json:
        return handle_unauthorized_access()
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ================================
# SECURITY MIDDLEWARE
# ================================

@app.before_request
def before_request():
    """
    Security middleware for each request
    """
    # Set security headers
    if not request.headers.get('X-Content-Type-Options'):
        request.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Validate session for authenticated users
    if current_user.is_authenticated:
        from rbac_system import validate_session
        if not validate_session():
            return redirect(url_for('auth.login'))

@app.after_request
def after_request(response):
    """
    Security headers after each request
    """
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Remove server information
    response.headers['Server'] = 'EduGuard'
    
    return response

# ================================
# MAIN ROUTES
# ================================

@app.route('/')
def index():
    """Main landing page"""
    if current_user.is_authenticated:
        from rbac_system import secure_redirect
        return secure_redirect('dashboard')
    
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Role-based dashboard redirect"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    from rbac_system import is_admin, is_student, is_faculty
    
    if is_admin():
        return redirect(url_for('admin.dashboard'))
    elif is_student():
        return redirect(url_for('student.dashboard'))
    elif is_faculty():
        return redirect(url_for('faculty.dashboard'))
    else:
        return redirect(url_for('auth.login'))

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    }

# ================================
# CONTEXT PROCESSORS
# ================================

@app.context_processor
def inject_user_data():
    """Inject user data into all templates"""
    return {
        'current_user': current_user,
        'is_admin': current_user.is_authenticated and current_user.role == 'admin',
        'is_student': current_user.is_authenticated and current_user.role == 'student',
        'is_faculty': current_user.is_authenticated and current_user.role == 'faculty'
    }

# ================================
# DATABASE INITIALIZATION
# ================================

def init_database():
    """Initialize database with required tables"""
    with app.app_context():
        try:
            # Import all models
            from models import User, Student, Attendance, RiskProfile, Alert
            from models_support import StudentGoal, MoodLog
            
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully")
            
            # Create default admin if not exists
            admin_user = User.query.filter_by(email='admin@eduguard.edu').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@eduguard.edu',
                    role='admin'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            db.session.rollback()

# ================================
# APPLICATION FACTORY
# ================================

def create_app(config_name='development'):
    """
    Application factory for different environments
    """
    app = Flask(__name__)
    
    # Shared core config required by extensions
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///eduguard.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600

    # Load configuration based on environment
    if config_name == 'production':
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_ECHO'] = False
        app.config['SESSION_COOKIE_SECURE'] = True
    else:
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_ECHO'] = True
        app.config['SESSION_COOKIE_SECURE'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    
    return app

# ================================
# MAIN EXECUTION
# ================================

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Development server
    print("🚀 Starting EduGuard with RBAC System")
    print("📊 Admin: http://127.0.0.1:5000/admin/dashboard")
    print("🎓 Student: http://127.0.0.1:5000/student/dashboard")
    print("🔐 Login: http://127.0.0.1:5000/auth/login")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=app.config.get('DEBUG', False)
    )
