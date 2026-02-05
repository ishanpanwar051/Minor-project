"""
Simple Seed Script for EduGuard System
Creates admin user and test data
"""

from app_fixed import app, db
from models import User, Student, Attendance, AcademicRecord, Intervention, RiskProfile, Alert
from datetime import datetime, date, timedelta
import random

def create_admin_user():
    """Create admin user"""
    with app.app_context():
        admin = User.query.filter_by(email='admin@university.edu').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@university.edu',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Created admin user: admin@university.edu / admin123")
        else:
            print("ℹ️ Admin user already exists")

def create_faculty_users():
    """Create faculty users"""
    with app.app_context():
        faculty_data = [
            ('prof_johnson', 'dr.johnson@university.edu', 'Dr. Robert Johnson'),
            ('prof_smith', 'prof.smith@university.edu', 'Prof. Emily Smith'),
            ('prof_williams', 'dr.williams@university.edu', 'Dr. Michael Williams'),
            ('prof_davis', 'prof.davis@university.edu', 'Prof. Sarah Davis')
        ]
        
        for username, email, name in faculty_data:
            faculty = User.query.filter_by(email=email).first()
            if not faculty:
                faculty = User(
                    username=username,
                    email=email,
                    role='faculty'
                )
                faculty.set_password('prof123')
                db.session.add(faculty)
                print(f"✅ Created faculty: {email}")
        
        db.session.commit()

def create_student_users():
    """Create student users"""
    with app.app_context():
        student_data = [
            ('student001', 'john.doe@university.edu', 'John Doe', 'CS101'),
            ('student002', 'jane.smith@university.edu', 'Jane Smith', 'CS102'),
            ('student003', 'mike.wilson@university.edu', 'Mike Wilson', 'CS103'),
            ('student004', 'sarah.brown@university.edu', 'Sarah Brown', 'CS104'),
            ('student005', 'alex.jones@university.edu', 'Alex Jones', 'CS105')
        ]
        
        for username, email, name, student_id in student_data:
            # Create user
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    username=username,
                    email=email,
                    role='student'
                )
                user.set_password('student123')
                db.session.add(user)
                db.session.commit()
                
                # Create student profile
                student = Student(
                    user_id=user.id,
                    student_id=student_id,
                    first_name=name.split()[0],
                    last_name=name.split()[1],
                    email=email,
                    department='Computer Science',
                    year=random.randint(1, 4),
                    semester=random.randint(1, 2),
                    gpa=round(random.uniform(2.0, 4.0), 2),
                    enrollment_date=date(2020, 9, 1),
                    credits_completed=random.randint(30, 120)
                )
                db.session.add(student)
                print(f"✅ Created student: {email}")
        
        db.session.commit()

if __name__ == '__main__':
    print("🌱 Creating seed data for EduGuard System...")
    
    try:
        create_admin_user()
        create_faculty_users()
        create_student_users()
        print("✅ Seed data created successfully!")
        
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
        print(f"❌ Error creating seed data: {e}")
