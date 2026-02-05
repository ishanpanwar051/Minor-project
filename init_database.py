"""
Database Initialization for EduGuard System
Fixes SQLAlchemy instance registration issues
"""

from app_fixed import app, db
from models import User, Student, Attendance, AcademicRecord, Intervention, RiskProfile, Alert
from datetime import datetime, date, timedelta
import hashlib

def init_database():
    """Initialize database with proper SQLAlchemy instance"""
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if admin user exists
            admin = User.query.filter_by(email='admin@university.edu').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@university.edu',
                    role='admin'
                )
                # Use simple SHA256 hash for consistency
                admin.password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
                db.session.add(admin)
                print("✅ Admin user created")
            else:
                print("ℹ️ Admin user already exists")
            
            # Check if faculty user exists
            faculty = User.query.filter_by(email='dr.johnson@university.edu').first()
            if not faculty:
                faculty = User(
                    username='prof_johnson',
                    email='dr.johnson@university.edu',
                    role='faculty'
                )
                faculty.password_hash = hashlib.sha256('prof123'.encode()).hexdigest()
                db.session.add(faculty)
                print("✅ Faculty user created")
            else:
                print("ℹ️ Faculty user already exists")
            
            # Check if student user exists
            student_user = User.query.filter_by(email='john.doe@university.edu').first()
            if not student_user:
                student_user = User(
                    username='student001',
                    email='john.doe@university.edu',
                    role='student'
                )
                student_user.password_hash = hashlib.sha256('student123'.encode()).hexdigest()
                db.session.add(student_user)
                
                # Create student profile
                student = Student(
                    user_id=student_user.id,
                    student_id='CS101',
                    first_name='John',
                    last_name='Doe',
                    email='john.doe@university.edu',
                    department='Computer Science',
                    year=2,
                    semester=1,
                    gpa=3.5,
                    enrollment_date=date(2022, 9, 1),
                    credits_completed=60
                )
                db.session.add(student)
                print("✅ Student user created")
            else:
                print("ℹ️ Student user already exists")
            
            db.session.commit()
            print("✅ Database initialization completed")
            
            print("\n🔐 LOGIN CREDENTIALS:")
            print("=" * 50)
            print("ADMIN LOGIN:")
            print("  Email: admin@university.edu")
            print("  Password: admin123")
            print("\nFACULTY LOGIN:")
            print("  Email: dr.johnson@university.edu")
            print("  Password: prof123")
            print("\nSTUDENT LOGIN:")
            print("  Email: john.doe@university.edu")
            print("  Password: student123")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_database()
