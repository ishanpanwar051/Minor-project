#!/usr/bin/env python3
"""
Test real-time functionality
"""

from app import create_app
from models import User, Student, Attendance, db
from datetime import date, timedelta

def test_realtime_data():
    app = create_app()
    with app.app_context():
        print("🔍 Testing Real-time Data Flow...")
        
        # Test 1: Check if students exist
        students = Student.query.all()
        print(f"✓ Total Students: {len(students)}")
        
        # Test 2: Check attendance data
        recent_attendance = Attendance.query.filter(
            Attendance.date >= date.today() - timedelta(days=7)
        ).all()
        print(f"✓ Recent Attendance Records: {len(recent_attendance)}")
        
        # Test 3: Check user mappings
        student_users = User.query.filter_by(role='student').all()
        print(f"✓ Student Users: {len(student_users)}")
        
        # Test 4: Create test attendance record
        if students:
            test_student = students[0]
            existing = Attendance.query.filter_by(
                student_id=test_student.id,
                date=date.today()
            ).first()
            
            if not existing:
                new_attendance = Attendance(
                    student_id=test_student.id,
                    date=date.today(),
                    status='Present',
                    course='Test Course'
                )
                db.session.add(new_attendance)
                db.session.commit()
                print(f"✓ Created test attendance for {test_student.first_name}")
            else:
                print(f"✓ Attendance already exists for {test_student.first_name}")
        
        # Test 5: Check dashboard stats API
        print("\n📊 Dashboard Stats Test:")
        total_students = Student.query.count()
        print(f"  - Total Students: {total_students}")
        
        # Test 6: Check student login credentials
        print("\n🔑 Student Login Test:")
        for i, student in enumerate(students[:3]):
            user = User.query.filter_by(email=student.email).first()
            if user:
                print(f"  {i+1}. {student.email} -> User ID: {user.id}, Role: {user.role}")
            else:
                print(f"  {i+1}. {student.email} -> NO USER FOUND")
        
        print("\n✅ Real-time data test completed!")

if __name__ == '__main__':
    test_realtime_data()
