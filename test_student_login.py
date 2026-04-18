#!/usr/bin/env python3
"""
Test script to check student login and navigation
"""

from models import User, Student
from app import create_app

def test_student_access():
    app = create_app()
    with app.app_context():
        # Check if students exist
        students = Student.query.all()
        print(f"Total Students: {len(students)}")
        
        student_users = User.query.filter_by(role='student').all()
        print(f"Student Users: {len(student_users)}")
        
        # Check specific student
        student = Student.query.filter_by(student_id='ST001').first()
        if student:
            print(f"Found student: {student.first_name} {student.last_name}")
            print(f"User ID: {student.user_id}")
            print(f"Email: {student.email}")
            
            # Check user account
            user = User.query.get(student.user_id)
            if user:
                print(f"User account: {user.email} (Role: {user.role})")
            else:
                print("No user account found!")
        else:
            print("No student with ID ST001 found")
            
        # Test support routes
        print("\nTesting support dashboard access...")
        for student_user in student_users[:3]:  # Test first 3 students
            student = Student.query.filter_by(user_id=student_user.id).first()
            if student:
                print(f"✓ {student_user.email} -> {student.first_name} {student.last_name}")
            else:
                print(f"✗ {student_user.email} -> No student profile")

if __name__ == '__main__':
    test_student_access()
