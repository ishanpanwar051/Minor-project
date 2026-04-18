"""
Create sample counselling data for testing
"""

from app import create_app
from models_enhanced import CounsellingRequest, db
from datetime import datetime, timedelta

def create_sample_counselling_data():
    """Create sample counselling requests for testing"""
    app = create_app()
    
    with app.app_context():
        print("Creating sample counselling data...")
        
        # Get Rohit's student ID
        from models import Student
        student = Student.query.filter_by(email='rohit.verma@eduguard.edu').first()
        
        if not student:
            print("Rohit student not found")
            return
        
        # Check if counselling requests already exist
        existing_requests = CounsellingRequest.query.filter_by(student_id=student.id).count()
        if existing_requests > 0:
            print(f"Counselling requests already exist: {existing_requests}")
            return
        
        # Create sample counselling requests
        counselling_requests = [
            CounsellingRequest(
                student_id=student.id,
                user_id=student.user_id,
                counselling_type='academic',
                topic='Career Guidance',
                description='I need help choosing between computer science and data science majors',
                priority='medium',
                preferred_date=datetime.utcnow() + timedelta(days=3),
                preferred_time='10:00 AM',
                duration_minutes=60,
                status='pending'
            ),
            CounsellingRequest(
                student_id=student.id,
                user_id=student.user_id,
                counselling_type='personal',
                topic='Study Stress Management',
                description='Feeling overwhelmed with coursework and need advice on time management',
                priority='high',
                preferred_date=datetime.utcnow() + timedelta(days=1),
                preferred_time='2:00 PM',
                duration_minutes=45,
                status='scheduled'
            )
        ]
        
        for request in counselling_requests:
            db.session.add(request)
        
        db.session.commit()
        print(f"Created {len(counselling_requests)} sample counselling requests")

if __name__ == '__main__':
    create_sample_counselling_data()
