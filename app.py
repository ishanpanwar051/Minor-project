"""
EduGuard Application
Clean, production-ready Flask application with real-time notifications
"""

from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_mail import Mail
from config import config
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
db = None
login_manager = LoginManager()
mail = Mail()
socketio = None

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from models import db
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Initialize real-time notifications
    global socketio
    try:
        from realtime_notifications import init_realtime_notifications
        socketio = init_realtime_notifications(app)
    except Exception as exc:
        logger.warning("Real-time notifications not available: %s", exc)
        socketio = None
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    def register_optional_blueprint(import_path, blueprint_name):
        """Keep optional modules from blocking the core admin/student panels."""
        try:
            module_name, object_name = import_path.rsplit('.', 1)
            module = __import__(module_name, fromlist=[object_name])
            app.register_blueprint(getattr(module, object_name))
        except Exception as exc:
            app.logger.warning(
                "Optional blueprint %s skipped: %s",
                blueprint_name,
                exc
            )
    
    # Register blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)
    
    # Register auth blueprint with RBAC
    from auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register scholarship system
    from scholarship_routes import scholarship_bp
    app.register_blueprint(scholarship_bp)
    
    # Register AI Dashboard
    from ai_dashboard_routes import ai_dashboard_bp
    app.register_blueprint(ai_dashboard_bp)
    
    # Optional student-support features. The core panels still load if one
    # optional integration is unavailable in a lightweight environment.
    register_optional_blueprint('ai_assistant_routes.ai_assistant_bp', 'AI Assistant')
    register_optional_blueprint('chatbot_routes.chatbot_bp', 'Chatbot')
    
    # Register Counselling System
    from counselling_routes import counselling_bp
    app.register_blueprint(counselling_bp)
    
    register_optional_blueprint('parent_routes.parent_bp', 'Parent Portal')
    register_optional_blueprint('support_routes.support_bp', 'Student Support')
    register_optional_blueprint('analysis_routes.analysis_bp', 'Analysis')
    register_optional_blueprint('update_routes.update_bp', 'Daily Updates')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        db.session.rollback()
        app.logger.error(f'Unhandled exception: {str(e)}')
        return render_template('errors/500.html'), 500
    
    # Global redirects
    @app.route('/login')
    def login_redirect():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    @app.route('/logout')
    def logout_redirect():
        from flask import redirect, url_for
        return redirect(url_for('auth.logout'))
    
    # Create database tables
    with app.app_context():
        try:
            # Import all models to ensure they're registered
            from models_parent import ParentMessage
            from models_support import StudentGoal, MoodLog
            
            db.create_all()
            apply_sqlite_schema_updates(app)
            app.logger.info('Database tables created successfully')
        except Exception as e:
            app.logger.error(f'Error creating database tables: {str(e)}')
    
    return app

def apply_sqlite_schema_updates(app):
    """Add new model columns to older local SQLite databases without deleting data."""
    from models import db
    from sqlalchemy import inspect, text

    if db.engine.dialect.name != 'sqlite':
        return

    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    for table in db.metadata.sorted_tables:
        if table.name not in existing_tables:
            continue

        existing_columns = {column['name'] for column in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing_columns or column.primary_key:
                continue

            column_type = column.type.compile(dialect=db.engine.dialect)
            db.session.execute(
                text(f'ALTER TABLE {table.name} ADD COLUMN {column.name} {column_type}')
            )
            app.logger.info('Added missing SQLite column: %s.%s', table.name, column.name)

    if 'users' in existing_tables:
        user_columns = {column['name'] for column in inspect(db.engine).get_columns('users')}
        if 'is_active' in user_columns:
            db.session.execute(text('UPDATE users SET is_active = 1 WHERE is_active IS NULL'))

    enum_normalizations = {
        'scholarships': {
            'draft': 'DRAFT',
            'active': 'ACTIVE',
            'closed': 'CLOSED',
            'expired': 'EXPIRED',
        },
        'scholarship_applications': {
            'pending': 'PENDING',
            'under_review': 'UNDER_REVIEW',
            'approved': 'APPROVED',
            'rejected': 'REJECTED',
            'withdrawn': 'WITHDRAWN',
        },
        'counselling_requests': {
            'requested': 'REQUESTED',
            'scheduled': 'SCHEDULED',
            'completed': 'COMPLETED',
            'cancelled': 'CANCELLED',
        },
    }

    for table_name, replacements in enum_normalizations.items():
        if table_name not in existing_tables:
            continue
        table_columns = {column['name'] for column in inspect(db.engine).get_columns(table_name)}
        if 'status' not in table_columns:
            continue
        for old_value, new_value in replacements.items():
            db.session.execute(
                text(f'UPDATE {table_name} SET status = :new_value WHERE status = :old_value'),
                {'old_value': old_value, 'new_value': new_value}
            )

    db.session.commit()

def run_app():
    """Run the application with SocketIO if available"""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if app.config.get('DEBUG', False) else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create initial data
    with app.app_context():
        create_initial_data()
    
    print("\nEduGuard Enhanced Application Starting...")
    print("Access at: http://127.0.0.1:5001")
    print(f"Debug mode: {app.config.get('DEBUG', False)}")
    print(f"Real-time notifications: {'Enabled' if socketio else 'Disabled'}")
    
    if socketio:
        # Run with SocketIO for real-time features
        socketio.run(
            app,
            debug=app.config.get('DEBUG', False),
            host='0.0.0.0',
            port=5001,
            allow_unsafe_werkzeug=True
        )
    else:
        # Run without SocketIO
        app.run(
            debug=app.config.get('DEBUG', False),
            host='0.0.0.0',
            port=5001
        )

# Create app instance for direct running
def create_initial_data():
    """Create initial data for the application"""
    from models import User, Student, Attendance, RiskProfile, db
    from datetime import date, timedelta
    import hashlib
    import random
    
    try:
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@eduguard.edu').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@eduguard.edu',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created admin user")
        
        # Check if faculty user exists
        faculty = User.query.filter_by(email='faculty@eduguard.edu').first()
        if not faculty:
            faculty = User(
                username='faculty',
                email='faculty@eduguard.edu',
                role='faculty'
            )
            faculty.set_password('faculty123')
            db.session.add(faculty)
            print("Created faculty user")
        
        # Create sample students
        if Student.query.count() < 5:
            sample_students = [
                ('ST001', 'John', 'Doe', 'john.doe@eduguard.edu', 'Computer Science'),
                ('ST002', 'Jane', 'Smith', 'jane.smith@eduguard.edu', 'Engineering'),
                ('ST003', 'Mike', 'Johnson', 'mike.johnson@eduguard.edu', 'Business'),
                ('ST004', 'Sarah', 'Williams', 'sarah.williams@eduguard.edu', 'Arts'),
                ('ST005', 'Alex', 'Brown', 'alex.brown@eduguard.edu', 'Science')
            ]
            
            for student_id, first_name, last_name, email, department in sample_students:
                # Create user
                student_user = User(
                    username=student_id.lower(),
                    email=email,
                    role='student'
                )
                student_user.set_password('student123')
                db.session.add(student_user)
                db.session.flush()  # Get the user ID
                
                # Create student profile
                student = Student(
                    user_id=student_user.id,
                    student_id=student_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    department=department,
                    year=2,
                    semester=1,
                    gpa=3.5,
                    enrollment_date=date(2022, 9, 1),
                    credits_completed=60,
                    parent_name=f"Parent of {first_name}",
                    parent_email=f"parent.{first_name.lower()}@example.com",
                    parent_phone="555-0100"
                )
                db.session.add(student)
                db.session.flush()  # Get the student ID
                
                # Create risk profile with random holistic factors
                financial = random.choice([True, False, False, False])
                family = random.choice([True, False, False, False])
                health = random.choice([True, False, False, False])
                isolation = random.choice([True, False, False, False])
                mental_score = random.randint(4, 10)
                
                risk_profile = RiskProfile(
                    student_id=student.id,
                    attendance_rate=85.0,
                    academic_performance=75.0,
                    financial_issues=financial,
                    family_problems=family,
                    health_issues=health,
                    social_isolation=isolation,
                    mental_wellbeing_score=mental_score
                )
                # Calculate initial risk score
                risk_profile.update_risk_score()
                
                db.session.add(risk_profile)
                
                # Create sample attendance records
                for i in range(30):
                    attendance_date = date.today() - timedelta(days=i)
                    status = random.choice(['Present', 'Present', 'Present', 'Absent', 'Late'])
                    attendance = Attendance(
                        student_id=student.id,
                        date=attendance_date,
                        status=status,
                        course=f'Course {random.randint(100, 999)}'
                    )
                    db.session.add(attendance)
            
            print("Created sample students with data")
        
        db.session.commit()

        if os.environ.get('EDUGUARD_DEMO_DATA', 'true').lower() != 'false':
            try:
                from demo_data import ensure_demo_data
                ensure_demo_data()
                print("Demo dashboard data synchronized")
            except Exception as demo_exc:
                print(f"Error creating demo dashboard data: {demo_exc}")
                db.session.rollback()

        print("Initial data created successfully")
        
        print("\nLOGIN CREDENTIALS:")
        print("=" * 50)
        print("ADMIN: admin@eduguard.edu / admin123")
        print("FACULTY: faculty@eduguard.edu / faculty123")
        print("STUDENT: john.doe@eduguard.edu / student123")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error creating initial data: {str(e)}")
        if db:
            db.session.rollback()

if __name__ == '__main__':
    run_app()
