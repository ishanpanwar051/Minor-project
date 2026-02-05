"""
EduGuard Clean Database Setup
Reset and initialize database with sample data
"""

import os
from app import create_app
from models import db, User, Student, Attendance, RiskProfile
from datetime import date, timedelta
import hashlib
import random

def clean_setup():
    """Clean setup - remove existing database and create fresh data"""
    # Remove existing database file
    db_file = 'eduguard.db'
    if os.path.exists(db_file):
        os.remove(db_file)
        print("✅ Removed existing database")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@eduguard.edu',
                role='admin'
            )
            admin.password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            db.session.add(admin)
            print("✅ Created admin user")
            
            # Create faculty user
            faculty = User(
                username='faculty',
                email='faculty@eduguard.edu',
                role='faculty'
            )
            faculty.password_hash = hashlib.sha256('faculty123'.encode()).hexdigest()
            db.session.add(faculty)
            print("✅ Created faculty user")
            
            # Create sample students
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
                student_user.password_hash = hashlib.sha256('student123'.encode()).hexdigest()
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
                    credits_completed=60
                )
                db.session.add(student)
                db.session.flush()  # Get the student ID
                
                # Create risk profile
                risk_profile = RiskProfile(
                    student_id=student.id,
                    risk_score=25.0,
                    risk_level='Low',
                    attendance_rate=85.0,
                    academic_performance=75.0
                )
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
            print("✅ Database setup completed successfully")
            
            print("\n🔐 LOGIN CREDENTIALS:")
            print("=" * 50)
            print("ADMIN: admin@eduguard.edu / admin123")
            print("FACULTY: faculty@eduguard.edu / faculty123")
            print("STUDENT: john.doe@eduguard.edu / student123")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error setting up database: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    clean_setup()
