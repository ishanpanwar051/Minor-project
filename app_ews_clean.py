"""
Enhanced Application Factory for Early Warning System (EWS)
Flask application factory with blueprints, extensions, and middleware
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_talisman import Talisman
from flask_migrate import Migrate
import logging
import os
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
mail = Mail()
migrate = Migrate()
talisman = Talisman()

def create_app(config_name=None):
    """
    Application factory pattern for Early Warning System
    
    Args:
        config_name: Configuration name (development, testing, production, staging)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    from config_ews import get_config
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Talisman for security headers (only in production)
    if app.config.get('SESSION_COOKIE_SECURE'):
        talisman.init_app(app, force_https=True)
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            from models_ews import User
            return User.query.get(int(user_id))
        except:
            return None
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Apply security headers
    apply_security_headers(app)
    
    # Initialize configuration
    config_class.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Initialize background tasks
    if app.config.get('BACKGROUND_TASKS_ENABLED'):
        initialize_background_tasks(app)
    
    return app

def register_blueprints(app):
    """Register application blueprints"""
    try:
        # Main routes
        from routes_ews.main import main_bp
        app.register_blueprint(main_bp)
        
        # Authentication routes
        from routes_ews.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        
        # API routes
        from routes_ews.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api/v1')
        
        # Admin routes
        from routes_ews.admin import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # Teacher routes
        from routes_ews.teacher import teacher_bp
        app.register_blueprint(teacher_bp, url_prefix='/teacher')
        
        # Parent routes
        from routes_ews.parent import parent_bp
        app.register_blueprint(parent_bp, url_prefix='/parent')
        
        # Student routes
        from routes_ews.student import student_bp
        app.register_blueprint(student_bp, url_prefix='/student')
        
        app.logger.info('All blueprints registered successfully')
        
    except ImportError as e:
        app.logger.error(f"Error importing blueprints: {str(e)}")
        # Fallback to basic routes
        register_fallback_routes(app)

def register_fallback_routes(app):
    """Register fallback routes if blueprints are not available"""
    @app.route('/')
    def index():
        return "EduGuard Early Warning System - Basic Mode"
    
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "version": "1.0.0"}

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': str(error),
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'Resource not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'status_code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500

def register_cli_commands(app):
    """Register CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        from models_ews import db, User, UserRole
        
        # Create all tables
        db.create_all()
        
        # Create default admin user if not exists
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@eduguard.com')
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            admin_user = User(
                username='admin',
                email=admin_email,
                first_name='System',
                last_name='Administrator',
                role=UserRole.ADMIN
            )
            admin_user.set_password('Admin123!@2024')
            db.session.add(admin_user)
            db.session.commit()
            print(f"Created admin user: {admin_email}")
        else:
            print("Admin user already exists")
        
        print("Database initialized successfully.")
    
    @app.cli.command()
    def seed_db():
        """Seed the database with sample data."""
        from services_ews.student_service import StudentService
        from services_ews.auth_service import AuthenticationService
        from models_ews import UserRole
        import random
        from datetime import datetime, timedelta
        
        print("Seeding database with sample data...")
        
        # Create sample teachers
        teachers_data = [
            {
                'username': 'teacher1',
                'email': 'teacher1@eduguard.com',
                'password': 'Teacher123!@2024',
                'first_name': 'John',
                'last_name': 'Doe',
                'department': 'Computer Science'
            },
            {
                'username': 'teacher2',
                'email': 'teacher2@eduguard.com',
                'password': 'Teacher123!@2024',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'department': 'Mathematics'
            }
        ]
        
        for teacher_data in teachers_data:
            success, user, message = AuthenticationService.create_user(
                username=teacher_data['username'],
                email=teacher_data['email'],
                password=teacher_data['password'],
                role=UserRole.TEACHER,
                first_name=teacher_data['first_name'],
                last_name=teacher_data['last_name']
            )
            if success:
                user.department = teacher_data['department']
                db.session.commit()
                print(f"Created teacher: {teacher_data['email']}")
        
        # Create sample students
        students_data = [
            {
                'student_id': f'STU{random.randint(1000, 9999)}',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': f'alice.johnson{random.randint(1, 999)}@student.edu',
                'grade': '10',
                'section': 'A',
                'parent_guardian_name': 'Robert Johnson',
                'parent_guardian_phone': f'+str(random.randint(1000000000, 9999999999)) + "'",
                'parent_guardian_email': f'robert.johnson{random.randint(1, 999)}@parent.com'"
            },
            {
                'student_id': f'STU{random.randint(1000, 9999)}',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'email': f'bob.wilson{random.randint(1, 999)}@student.edu',
                'grade': '10',
                'section': 'B',
                'parent_guardian_name': 'Mary Wilson',
                'parent_guardian_phone': f'+str(random.randint(1000000000, 9999999999)) + "'",
                'parent_guardian_email': f'mary.wilson{random.randint(1, 999)}@parent.com'"
            },
            {
                'student_id': f'STU{random.randint(1000, 9999)}',
                'first_name': 'Carol',
                'last_name': 'Brown',
                'email': f'carol.brown{random.randint(1, 999)}@student.edu',
                'grade': '11',
                'section': 'A',
                'parent_guardian_name': 'David Brown',
                'parent_guardian_phone': f'+str(random.randint(1000000000, 9999999999)) + "'",
                'parent_guardian_email': f'david.brown{random.randint(1, 999)}@parent.com'"
            }
        ]
        
        for student_data in students_data:
            success, student, message = StudentService.create_student(
                student_data=student_data,
                creator_id=1  # Admin user
            )
            if success:
                print(f"Created student: {student_data['email']}")
        
        db.session.commit()
        print("Database seeded successfully!")
    
    @app.cli.command()
    def update_risk_scores():
        """Update risk scores for all students."""
        from services_ews.risk_service import RiskCalculationService
        
        print("Updating risk scores for all students...")
        result = RiskCalculationService.batch_update_risk_scores()
        
        print(f"Risk update completed:")
        print(f"  Total students: {result['total_students']}")
        print(f"  Updated: {result['updated_count']}")
        print(f"  Failed: {result['failed_count']}")
        
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")
    
    @app.cli.command()
    def create_admin():
        """Create admin user interactively."""
        import getpass
        
        print("Create Admin User")
        print("-" * 30)
        
        username = input("Username: ")
        email = input("Email: ")
        password = getpass.getpass("Password: ")
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        
        from services_ews.auth_service import AuthenticationService
        from models_ews import UserRole
        
        success, user, message = AuthenticationService.create_user(
            username=username,
            email=email,
            password=password,
            role=UserRole.ADMIN,
            first_name=first_name,
            last_name=last_name
        )
        
        if success:
            print(f"✅ Admin user created successfully: {email}")
        else:
            print(f"❌ Failed to create user: {message}")
    
    @app.cli.command()
    def run_ml_training():
        """Run ML model training."""
        from services_ews.ml_service import MLService
        
        print("Starting ML model training...")
        result = MLService.train_model()
        
        if result['success']:
            print(f"✅ Model training completed successfully!")
            print(f"  Accuracy: {result['accuracy']:.2f}%")
            print(f"  Model saved to: {result['model_path']}")
        else:
            print(f"❌ Model training failed: {result['error']}")
    
    @app.cli.command()
    def run_background_tasks():
        """Run all background tasks immediately."""
        from services_ews.background_tasks import BackgroundTaskService
        
        print("Running all background tasks...")
        results = BackgroundTaskService.run_all_tasks()
        
        print("Background tasks completed:")
        for task_name, result in results.items():
            print(f"  {task_name}: {result}")

# Create app instance for development
app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
