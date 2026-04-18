"""
Complete Dashboard Debugging Script
Tests all components systematically
"""

from app import create_app
from models import db
from sqlalchemy import text
from datetime import datetime, timedelta

def debug_dashboard_complete():
    """Debug all dashboard components"""
    app = create_app()
    
    with app.app_context():
        print("=== COMPLETE DASHBOARD DEBUG ===")
        
        # Test 1: Check if student exists
        print("\n1. STUDENT DATA CHECK")
        result = db.session.execute(text("SELECT id, first_name, last_name, email, gpa FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
        student_row = result.fetchone()
        
        if student_row:
            print(f"   Student found: {student_row[1]} {student_row[2]} (ID: {student_row[0]})")
            print(f"   GPA: {student_row[4]}, Email: {student_row[3]}")
        else:
            print("   Student NOT found - creating...")
            # Create student
            result = db.session.execute(text("SELECT id FROM users WHERE email = 'rohit.verma@eduguard.edu'"))
            user_row = result.fetchone()
            
            if user_row:
                db.session.execute(text('''
                    INSERT INTO students (user_id, student_id, first_name, last_name, email, gpa, department, year, semester)
                    VALUES (:user_id, :student_id, :first_name, :last_name, :email, :gpa, :department, :year, :semester)
                '''), {
                    'user_id': user_row[0],
                    'student_id': f"STU{user_row[0]}",
                    'first_name': 'Rohit',
                    'last_name': 'Verma',
                    'email': 'rohit.verma@eduguard.edu',
                    'gpa': 7.0,
                    'department': 'CSE',
                    'year': 1,
                    'semester': 1
                })
                db.session.commit()
                print("   Student created successfully")
            else:
                print("   User not found - cannot create student")
                return
        
        # Test 2: Check scholarships
        print("\n2. SCHOLARSHIPS DATA CHECK")
        result = db.session.execute(text("SELECT COUNT(*) FROM scholarships WHERE status = 'active'"))
        scholarship_count = result.fetchone()[0]
        print(f"   Active scholarships: {scholarship_count}")
        
        if scholarship_count == 0:
            print("   Creating sample scholarships...")
            scholarships = [
                ('Merit Scholarship', 'EduGuard Foundation', 5000, 3.5),
                ('STEM Grant', 'Tech Fund', 3000, 3.0),
                ('Community Award', 'Local Board', 2000, 2.8)
            ]
            
            for title, provider, amount, min_gpa in scholarships:
                db.session.execute(text('''
                    INSERT INTO scholarships (title, provider, amount, currency, description, min_gpa, status, application_deadline)
                    VALUES (:title, :provider, :amount, 'USD', :description, :min_gpa, 'active', :deadline)
                '''), {
                    'title': title,
                    'provider': provider,
                    'amount': amount,
                    'description': f'Sample scholarship: {title}',
                    'min_gpa': min_gpa,
                    'deadline': datetime.utcnow() + timedelta(days=60)
                })
            
            db.session.commit()
            print("   Sample scholarships created")
        
        # Test 3: Check applications
        print("\n3. APPLICATIONS DATA CHECK")
        result = db.session.execute(text("SELECT COUNT(*) FROM scholarship_applications"))
        app_count = result.fetchone()[0]
        print(f"   Scholarship applications: {app_count}")
        
        if app_count == 0:
            print("   Creating sample applications...")
            # Get student and scholarship IDs
            result = db.session.execute(text("SELECT id FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
            student_id = result.fetchone()[0]
            
            result = db.session.execute(text("SELECT id FROM scholarships LIMIT 2"))
            scholarship_ids = [row[0] for row in result.fetchall()]
            
            for i, scholarship_id in enumerate(scholarship_ids):
                db.session.execute(text('''
                    INSERT INTO scholarship_applications 
                    (student_id, scholarship_id, status, application_date, gpa_at_application, ai_eligibility_score, ai_success_probability)
                    VALUES (:student_id, :scholarship_id, :status, :application_date, :gpa_at_application, :ai_eligibility_score, :ai_success_probability)
                '''), {
                    'student_id': student_id,
                    'scholarship_id': scholarship_id,
                    'status': 'approved' if i == 0 else 'pending',
                    'application_date': datetime.utcnow() - timedelta(days=i*5),
                    'gpa_at_application': 7.0,
                    'ai_eligibility_score': 85.0 + i*5,
                    'ai_success_probability': 0.75 + i*0.1
                })
            
            db.session.commit()
            print("   Sample applications created")
        
        # Test 4: Check counselling
        print("\n4. COUNSELLING DATA CHECK")
        result = db.session.execute(text("SELECT COUNT(*) FROM counselling_requests"))
        counselling_count = result.fetchone()[0]
        print(f"   Counselling requests: {counselling_count}")
        
        if counselling_count == 0:
            print("   Creating sample counselling requests...")
            result = db.session.execute(text("SELECT id FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
            student_id = result.fetchone()[0]
            
            requests = [
                ('academic', 'Career Guidance', 'Need help choosing major'),
                ('personal', 'Study Stress', 'Feeling overwhelmed')
            ]
            
            for req_type, topic, desc in requests:
                db.session.execute(text('''
                    INSERT INTO counselling_requests 
                    (student_id, user_id, counselling_type, topic, description, priority, status, request_date)
                    VALUES (:student_id, :user_id, :counselling_type, :topic, :description, :priority, :status, :request_date)
                '''), {
                    'student_id': student_id,
                    'user_id': student_id,
                    'counselling_type': req_type,
                    'topic': topic,
                    'description': desc,
                    'priority': 'medium',
                    'status': 'pending',
                    'request_date': datetime.utcnow() - timedelta(days=1)
                })
            
            db.session.commit()
            print("   Sample counselling requests created")
        
        # Test 5: Check attendance
        print("\n5. ATTENDANCE DATA CHECK")
        result = db.session.execute(text("SELECT COUNT(*) FROM attendance"))
        attendance_count = result.fetchone()[0]
        print(f"   Attendance records: {attendance_count}")
        
        if attendance_count == 0:
            print("   Creating sample attendance records...")
            result = db.session.execute(text("SELECT id FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
            student_id = result.fetchone()[0]
            
            for i in range(30):
                date = datetime.utcnow() - timedelta(days=i)
                status = 'Present' if i % 7 != 0 else 'Absent'
                
                db.session.execute(text('''
                    INSERT INTO attendance (student_id, date, status)
                    VALUES (:student_id, :date, :status)
                '''), {
                    'student_id': student_id,
                    'date': date.date(),
                    'status': status
                })
            
            db.session.commit()
            print("   Sample attendance records created")
        
        # Test 6: Final data summary
        print("\n6. FINAL DATA SUMMARY")
        result = db.session.execute(text("SELECT COUNT(*) FROM scholarships"))
        print(f"   Scholarships: {result.fetchone()[0]}")
        
        result = db.session.execute(text("SELECT COUNT(*) FROM scholarship_applications"))
        print(f"   Applications: {result.fetchone()[0]}")
        
        result = db.session.execute(text("SELECT COUNT(*) FROM counselling_requests"))
        print(f"   Counselling requests: {result.fetchone()[0]}")
        
        result = db.session.execute(text("SELECT COUNT(*) FROM attendance"))
        print(f"   Attendance records: {result.fetchone()[0]}")
        
        result = db.session.execute(text("SELECT COUNT(*) FROM students"))
        print(f"   Students: {result.fetchone()[0]}")
        
        print("\n=== DEBUG COMPLETE ===")
        print("Dashboard should now have data to display!")

if __name__ == '__main__':
    debug_dashboard_complete()
