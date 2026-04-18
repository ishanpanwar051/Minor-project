#!/usr/bin/env python3
"""
Fix student user mappings and create missing student accounts
"""

from models import User, Student, db
from app import create_app
from datetime import date

def fix_student_mappings():
    app = create_app()
    with app.app_context():
        # Get all students
        students = Student.query.all()
        print(f"Found {len(students)} students")
        
        # Get all student users
        student_users = User.query.filter_by(role='student').all()
        print(f"Found {len(student_users)} student users")
        
        # Create missing user accounts for students
        for student in students:
            user = User.query.filter_by(email=student.email).first()
            if not user:
                # Create user account for student
                user = User(
                    username=student.student_id.lower(),
                    email=student.email,
                    role='student'
                )
                user.set_password('student123')
                db.session.add(user)
                db.session.flush()
                
                # Update student with user_id
                student.user_id = user.id
                print(f"✓ Created user for {student.first_name} {student.last_name} ({student.email})")
            else:
                # Update existing user mapping
                if student.user_id != user.id:
                    student.user_id = user.id
                    print(f"✓ Updated mapping for {student.first_name} {student.last_name}")
        
        try:
            db.session.commit()
            print("✅ Student mappings fixed successfully!")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
        
        # Test the fix
        print("\nTesting student access...")
        test_students = Student.query.limit(3).all()
        for student in test_students:
            user = User.query.get(student.user_id)
            if user:
                print(f"✓ {student.first_name} -> User: {user.email} (Role: {user.role})")
            else:
                print(f"✗ {student.first_name} -> No user found")

if __name__ == '__main__':
    fix_student_mappings()
