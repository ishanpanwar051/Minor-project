from app import create_app
from models import db, User, Student, RiskProfile
from flask_login import login_user
import traceback

app = create_app()

with app.app_context():
    try:
        print("Checking tables...")
        inspector = db.inspect(db.engine)
        print(f"Tables: {inspector.get_table_names()}")
        
        # Test a student user
        user = User.query.filter_by(role='student').first()
        if not user:
            print("No student user found. Creating one...")
            user = User(username='test_student', email='test@student.edu', role='student')
            user.set_password('student123')
            db.session.add(user)
            db.session.commit()
            print(f"Created student user: {user.id}")
        
        print(f"Testing dashboard logic for user {user.id} ({user.email})")
        
        # Simulate student_dashboard logic
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            print("Creating student profile...")
            student = Student(
                user_id=user.id,
                student_id=f"STU{user.id}",
                first_name="Test",
                last_name="Student",
                email=user.email,
                gpa=7.5,
                department="CSE",
                year=1,
                semester=1
            )
            db.session.add(student)
            db.session.commit()
            print("Student profile created.")

        risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
        if not risk_profile:
            print("Creating risk profile...")
            risk_profile = RiskProfile(
                student_id=student.id,
                attendance_rate=80.0,
                academic_performance=student.gpa * 10
            )
            db.session.add(risk_profile)
            db.session.commit()
            print("Risk profile created.")

        # Test the raw SQL queries
        from sqlalchemy import text
        print("Testing counselling_requests query...")
        db.session.execute(text("SELECT * FROM counselling_requests")).fetchall()
        print("Testing scholarships query...")
        db.session.execute(text("SELECT * FROM scholarships")).fetchall()
        print("Testing scholarship_applications query...")
        db.session.execute(text("SELECT * FROM scholarship_applications")).fetchall()
        
        print("All dashboard queries passed!")
        
    except Exception as e:
        print(f"FAILED with error: {str(e)}")
        traceback.print_exc()
