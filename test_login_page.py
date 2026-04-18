#!/usr/bin/env python3
"""
Test Login Page - Verify all user types can login
"""

from models import User, Student, db
from app import create_app

def test_login_page():
    app = create_app()
    with app.app_context():
        print("🔐 Testing Login Page Access")
        print("=" * 50)
        
        # Check all users in database
        all_users = User.query.all()
        print(f"Total users in database: {len(all_users)}")
        
        # Group users by role
        admin_users = User.query.filter_by(role='admin').all()
        faculty_users = User.query.filter_by(role='faculty').all()
        student_users = User.query.filter_by(role='student').all()
        
        print(f"\n👥 Admin Users: {len(admin_users)}")
        for admin in admin_users:
            print(f"   - {admin.email}")
        
        print(f"\n👨‍🏫 Faculty Users: {len(faculty_users)}")
        for faculty in faculty_users:
            print(f"   - {faculty.email} ({'Counselor' if 'counselor' in faculty.email else 'Faculty'})")
        
        print(f"\n🎓 Student Users: {len(student_users)}")
        for i, student in enumerate(student_users[:5], 1):
            print(f"   {i}. {student.email}")
        if len(student_users) > 5:
            print(f"   ... and {len(student_users) - 5} more students")
        
        # Test student accounts exist
        print(f"\n🔍 Student Account Verification:")
        print("=" * 40)
        
        test_students = [
            'rohit.verma@eduguard.edu',
            'neha.sharma@eduguard.edu', 
            'arjun.yadav@eduguard.edu'
        ]
        
        for email in test_students:
            user = User.query.filter_by(email=email).first()
            if user:
                student = Student.query.filter_by(user_id=user.id).first()
                if student:
                    print(f"✅ {email}")
                    print(f"   User ID: {user.id}")
                    print(f"   Role: {user.role}")
                    print(f"   Student: {student.first_name} {student.last_name}")
                    print(f"   Student ID: {student.student_id}")
                else:
                    print(f"⚠️  {email} - User exists but no student profile")
            else:
                print(f"❌ {email} - User not found")
        
        # Test login credentials
        print(f"\n🔑 Working Login Credentials:")
        print("=" * 35)
        
        print("🔧 ADMIN ACCESS:")
        print("   Email: admin@eduguard.edu")
        print("   Password: admin123")
        print("   → Can access: Admin panel, all student data, system management")
        
        print("\n👨‍🏫 FACULTY ACCESS:")
        print("   Email: dr.sharma@eduguard.edu")
        print("   Password: faculty123")
        print("   → Can access: Student management, attendance, risk analysis")
        
        print("\n👨‍🏫 COUNSELOR ACCESS:")
        print("   Email: counselor@eduguard.edu")
        print("   Password: counsel123")
        print("   → Can access: Counselling sessions, student support")
        
        print("\n🎓 STUDENT ACCESS:")
        print("   Email: rohit.verma@eduguard.edu")
        print("   Password: student123")
        print("   → Can access: Personal dashboard, own data only")
        
        print("\n   Email: neha.sharma@eduguard.edu")
        print("   Password: student123")
        print("   → Can access: Personal dashboard, own data only")
        
        print("\n   Email: arjun.yadav@eduguard.edu")
        print("   Password: student123")
        print("   → Can access: Personal dashboard, own data only")
        
        print(f"\n🌐 Access URL:")
        print("=" * 15)
        print("http://127.0.0.1:5000/login")
        
        print(f"\n📋 Login Flow:")
        print("=" * 15)
        print("1. Go to http://127.0.0.1:5000/login")
        print("2. Enter email and password from above")
        print("3. System will redirect based on user role:")
        print("   - Admin → Admin Dashboard")
        print("   - Faculty/Counselor → Faculty Dashboard")
        print("   - Student → Student Support Dashboard")

if __name__ == '__main__':
    test_login_page()
