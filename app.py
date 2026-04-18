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
    except ImportError:
        logger.warning("Real-time notifications not available")
        socketio = None
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
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
    
    # Register AI Assistant
    from ai_assistant_routes import ai_assistant_bp
    app.register_blueprint(ai_assistant_bp)
    
    # Register Counselling System
    from counselling_routes import counselling_bp
    app.register_blueprint(counselling_bp)
    
    # Register parent blueprint
    from parent_routes import parent_bp
    app.register_blueprint(parent_bp)
    
    # Register support blueprint
    from support_routes import support_bp
    app.register_blueprint(support_bp)
    
    # Register analysis blueprint
    from analysis_routes import analysis_bp
    app.register_blueprint(analysis_bp)
    
    # Register daily update system
    from update_routes import update_bp
    app.register_blueprint(update_bp)
    
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
    
    # Create database tables
    with app.app_context():
        try:
            # Import all models to ensure they're registered
            from models_parent import ParentMessage
            from models_support import StudentGoal, MoodLog
            
            db.create_all()
            app.logger.info('Database tables created successfully')
        except Exception as e:
            app.logger.error(f'Error creating database tables: {str(e)}')
    
    return app

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
    
    print("\n🚀 EduGuard Enhanced Application Starting...")
    print(f"🌐 Access at: http://127.0.0.1:5000")
    print(f"🔧 Debug mode: {app.config.get('DEBUG', False)}")
    print(f"🤖 ML Model: {'Enabled' if socketio else 'Disabled'}")
    
    if socketio:
        # Run with SocketIO for real-time features
        socketio.run(
            app,
            debug=app.config.get('DEBUG', False),
            host='0.0.0.0',
            port=5000
        )
    else:
        # Run without SocketIO
        app.run(
            debug=app.config.get('DEBUG', False),
            host='0.0.0.0',
            port=5000
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
            print("✅ Created admin user")
        
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
            print("✅ Created faculty user")
        
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
            
            print("✅ Created sample students with data")
        
        db.session.commit()
        print("✅ Initial data created successfully")
        
        print("\n🔐 LOGIN CREDENTIALS:")
        print("=" * 50)
        print("ADMIN: admin@eduguard.edu / admin123")
        print("FACULTY: faculty@eduguard.edu / faculty123")
        print("STUDENT: john.doe@eduguard.edu / student123")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error creating initial data: {str(e)}")
        if db:
            db.session.rollback()

if __name__ == '__main__':
    run_app()
