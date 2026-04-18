"""
Create sample data for dashboard testing
"""

from app import create_app
from models import db
from sqlalchemy import text
from datetime import datetime, timedelta

def create_sample_dashboard_data():
    """Create sample data for dashboard"""
    app = create_app()
    
    with app.app_context():
        print("Creating sample dashboard data...")
        
        # Check if scholarships table exists and has data
        result = db.session.execute(text("SELECT COUNT(*) FROM scholarships"))
        scholarship_count = result.fetchone()[0]
        
        if scholarship_count == 0:
            print("Creating sample scholarships...")
            scholarships_data = [
                {
                    'title': 'Merit Scholarship for Excellence',
                    'provider': 'EduGuard Foundation',
                    'amount': 5000,
                    'currency': 'USD',
                    'description': 'Awarded to students with outstanding academic performance and leadership qualities',
                    'min_gpa': 3.5,
                    'status': 'active',
                    'deadline': datetime.utcnow() + timedelta(days=60)
                },
                {
                    'title': 'STEM Innovation Grant',
                    'provider': 'Tech Education Fund',
                    'amount': 3000,
                    'currency': 'USD',
                    'description': 'Support for students pursuing careers in science, technology, engineering, and mathematics',
                    'min_gpa': 3.0,
                    'status': 'active',
                    'deadline': datetime.utcnow() + timedelta(days=45)
                },
                {
                    'title': 'Community Service Scholarship',
                    'provider': 'Local Education Board',
                    'amount': 2000,
                    'currency': 'USD',
                    'description': 'Recognizes students who demonstrate exceptional commitment to community service',
                    'min_gpa': 2.8,
                    'status': 'active',
                    'deadline': datetime.utcnow() + timedelta(days=30)
                }
            ]
            
            for scholarship in scholarships_data:
                db.session.execute(text('''
                    INSERT INTO scholarships 
                    (title, provider, amount, currency, description, min_gpa, status, application_deadline)
                    VALUES (:title, :provider, :amount, :currency, :description, :min_gpa, :status, :deadline)
                '''), scholarship)
            
            db.session.commit()
            print(f"Created {len(scholarships_data)} sample scholarships")
        else:
            print(f"Scholarships already exist: {scholarship_count}")
        
        # Check if scholarship_applications table has data
        result = db.session.execute(text("SELECT COUNT(*) FROM scholarship_applications"))
        application_count = result.fetchone()[0]
        
        if application_count == 0:
            print("Creating sample applications...")
            # Get Rohit's student ID
            result = db.session.execute(text("SELECT id FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
            student_row = result.fetchone()
            
            if student_row:
                student_id = student_row[0]
                
                # Get scholarship IDs
                result = db.session.execute(text("SELECT id FROM scholarships LIMIT 2"))
                scholarship_ids = [row[0] for row in result.fetchall()]
                
                applications_data = [
                    {
                        'student_id': student_id,
                        'scholarship_id': scholarship_ids[0] if len(scholarship_ids) > 0 else 1,
                        'status': 'pending',
                        'application_date': datetime.utcnow() - timedelta(days=5),
                        'gpa_at_application': 7.0,
                        'ai_eligibility_score': 85.0,
                        'ai_success_probability': 0.75
                    },
                    {
                        'student_id': student_id,
                        'scholarship_id': scholarship_ids[1] if len(scholarship_ids) > 1 else 2,
                        'status': 'approved',
                        'application_date': datetime.utcnow() - timedelta(days=15),
                        'gpa_at_application': 7.0,
                        'ai_eligibility_score': 90.0,
                        'ai_success_probability': 0.85
                    }
                ]
                
                for app in applications_data:
                    db.session.execute(text('''
                        INSERT INTO scholarship_applications 
                        (student_id, scholarship_id, status, application_date, gpa_at_application, ai_eligibility_score, ai_success_probability)
                        VALUES (:student_id, :scholarship_id, :status, :application_date, :gpa_at_application, :ai_eligibility_score, :ai_success_probability)
                    '''), app)
                
                db.session.commit()
                print(f"Created {len(applications_data)} sample applications")
            else:
                print("Student not found")
        else:
            print(f"Applications already exist: {application_count}")
        
        # Check if attendance records exist
        result = db.session.execute(text("SELECT COUNT(*) FROM attendance"))
        attendance_count = result.fetchone()[0]
        
        if attendance_count == 0:
            print("Creating sample attendance records...")
            # Get Rohit's student ID
            result = db.session.execute(text("SELECT id FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
            student_row = result.fetchone()
            
            if student_row:
                student_id = student_row[0]
                
                # Create attendance records for the last 30 days
                for i in range(30):
                    date = datetime.utcnow() - timedelta(days=i)
                    status = 'Present' if i % 7 != 0 else 'Absent'  # 1 absent per week
                    
                    db.session.execute(text('''
                        INSERT INTO attendance (student_id, date, status)
                        VALUES (:student_id, :date, :status)
                    '''), {
                        'student_id': student_id,
                        'date': date.date(),
                        'status': status
                    })
                
                db.session.commit()
                print(f"Created 30 sample attendance records")
            else:
                print("Student not found")
        else:
            print(f"Attendance records already exist: {attendance_count}")
        
        print("Sample dashboard data creation completed!")

if __name__ == '__main__':
    create_sample_dashboard_data()
