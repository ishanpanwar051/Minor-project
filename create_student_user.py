from app import create_app, db
from models import User, Student
from datetime import datetime

def create_student_user():
    app = create_app()
    with app.app_context():
        # Check if student user exists
        existing_user = User.query.filter_by(email='rohit.verma@eduguard.edu').first()
        if existing_user:
            print('Student user already exists')
            return
        
        # Create user
        user = User(
            email='rohit.verma@eduguard.edu',
            role='student',
            is_active=True
        )
        user.set_password('student123')
        db.session.add(user)
        db.session.flush()
        
        # Create student profile
        student = Student(
            user_id=user.id,
            first_name='Rohit',
            last_name='Verma',
            email='rohit.verma@eduguard.edu',
            gpa=3.8,
            enrollment_date=datetime.now(),
            academic_year='2023-2024',
            department='Computer Science',
            semester=6,
            credits_completed=90,
            current_gpa=3.8
        )
        db.session.add(student)
        db.session.commit()
        print('Student user created successfully!')
        print('Login: rohit.verma@eduguard.edu / student123')

if __name__ == '__main__':
    create_student_user()
