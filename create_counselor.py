#!/usr/bin/env python3
"""
Create Counselor User and Show System Structure
"""

from models import User, Student, Counselling, db
from app import create_app
from datetime import datetime

def create_counselor_and_show_structure():
    app = create_app()
    with app.app_context():
        print("🏫 EduGuard System Structure")
        print("=" * 50)
        
        # Check if counselor exists
        counselor = User.query.filter_by(email='counselor@eduguard.edu').first()
        if not counselor:
            counselor = User(
                username='counselor',
                email='counselor@eduguard.edu',
                role='faculty'  # Counselors are faculty type
            )
            counselor.set_password('counsel123')
            db.session.add(counselor)
            db.session.commit()
            print("✅ Created Counselor Account:")
            print(f"   Email: counselor@eduguard.edu")
            print(f"   Password: counsel123")
            print(f"   Role: {counselor.role}")
        else:
            print("✅ Counselor already exists:")
            print(f"   Email: {counselor.email}")
            print(f"   Role: {counselor.role}")
        
        print("\n👥 User Roles in System:")
        print("=" * 30)
        
        # Show all users by role
        admin_users = User.query.filter_by(role='admin').all()
        faculty_users = User.query.filter_by(role='faculty').all()
        student_users = User.query.filter_by(role='student').all()
        
        print(f"🔧 Admin Users: {len(admin_users)}")
        for admin in admin_users:
            print(f"   - {admin.email}")
        
        print(f"\n👨‍🏫 Faculty/Users: {len(faculty_users)}")
        for faculty in faculty_users:
            print(f"   - {faculty.email} ({'Counselor' if 'counselor' in faculty.email else 'Faculty'})")
        
        print(f"\n🎓 Student Users: {len(student_users)}")
        for i, student in enumerate(student_users[:5]):  # Show first 5
            print(f"   {i+1}. {student.email}")
        if len(student_users) > 5:
            print(f"   ... and {len(student_users) - 5} more students")
        
        print("\n📊 Student Data:")
        print("=" * 20)
        
        students = Student.query.all()
        print(f"Total Students: {len(students)}")
        
        # Show sample students
        for i, student in enumerate(students[:3]):
            print(f"\n{i+1}. {student.first_name} {student.last_name}")
            print(f"   ID: {student.student_id}")
            print(f"   Email: {student.email}")
            print(f"   Department: {student.department}")
            print(f"   Year: {student.year}")
            print(f"   GPA: {student.gpa}")
            
            # Check if has user account
            user = User.query.get(student.user_id) if student.user_id else None
            if user:
                print(f"   ✅ Has User Account: {user.email}")
            else:
                print(f"   ❌ No User Account")
        
        print("\n💬 Counselling System:")
        print("=" * 25)
        
        # Check counselling sessions
        counselling_sessions = Counselling.query.all()
        print(f"Total Counselling Sessions: {len(counselling_sessions)}")
        
        if counselling_sessions:
            for session in counselling_sessions[:3]:
                student = Student.query.get(session.student_id)
                counsellor = User.query.get(session.counsellor_id)
                print(f"\nSession {session.id}:")
                print(f"   Student: {student.first_name if student else 'Unknown'}")
                print(f"   Counselor: {counsellor.email if counsellor else 'Unknown'}")
                print(f"   Date: {session.session_date}")
                print(f"   Type: {session.session_type}")
                print(f"   Status: {session.status}")
        else:
            print("No counselling sessions found")
        
        print("\n🔐 Login Credentials:")
        print("=" * 25)
        print("🔧 ADMIN: admin@eduguard.edu / admin123")
        print("👨‍🏫 COUNSELOR: counselor@eduguard.edu / counsel123")
        print("👨‍🏫 FACULTY: dr.sharma@eduguard.edu / faculty123")
        print("🎓 STUDENT: rohit.verma@eduguard.edu / student123")
        print("🎓 STUDENT: neha.sharma@eduguard.edu / student123")
        print("🎓 STUDENT: arjun.yadav@eduguard.edu / student123")
        
        print("\n📋 System Flow:")
        print("=" * 15)
        print("1. Admin manages entire system")
        print("2. Faculty/Counselor manage students")
        print("3. Students access their support dashboard")
        print("4. Parents can view child's progress")
        print("5. AI provides risk analysis and recommendations")

if __name__ == '__main__':
    create_counselor_and_show_structure()
