"""
Create sample counselling data using direct SQL
"""

from app import create_app
from models import db
from sqlalchemy import text
from datetime import datetime, timedelta

def create_sample_counselling_data():
    """Create sample counselling requests using direct SQL"""
    app = create_app()
    
    with app.app_context():
        print("Creating sample counselling data...")
        
        # Create counselling_requests table if it doesn't exist
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS counselling_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                counselling_type VARCHAR(50),
                topic VARCHAR(200),
                description TEXT,
                priority VARCHAR(20) DEFAULT 'medium',
                preferred_date TIMESTAMP,
                preferred_time VARCHAR(20),
                duration_minutes INTEGER DEFAULT 60,
                status VARCHAR(20) DEFAULT 'pending',
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_counsellor_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assigned_counsellor_id) REFERENCES users (id)
            )
        '''))
        db.session.commit()
        print("Counselling requests table created/verified")
        
        # Get Rohit's student ID
        result = db.session.execute(text("SELECT id, user_id FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
        student_row = result.fetchone()
        
        if not student_row:
            print("Rohit student not found")
            return
        
        student_id, user_id = student_row
        
        # Check if counselling requests already exist
        result = db.session.execute(text("SELECT COUNT(*) FROM counselling_requests WHERE student_id = :student_id"), {"student_id": student_id})
        existing_count = result.fetchone()[0]
        
        if existing_count > 0:
            print(f"Counselling requests already exist: {existing_count}")
            return
        
        # Create sample counselling requests
        requests_data = [
            {
                'type': 'academic',
                'topic': 'Career Guidance',
                'description': 'I need help choosing between computer science and data science majors',
                'priority': 'medium',
                'date': (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
                'time': '10:00 AM',
                'duration': 60,
                'status': 'pending'
            },
            {
                'type': 'personal',
                'topic': 'Study Stress Management',
                'description': 'Feeling overwhelmed with coursework and need advice on time management',
                'priority': 'high',
                'date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'time': '2:00 PM',
                'duration': 45,
                'status': 'scheduled'
            }
        ]
        
        for req_data in requests_data:
            db.session.execute(text('''
                INSERT INTO counselling_requests 
                (student_id, user_id, counselling_type, topic, description, priority, preferred_date, preferred_time, duration_minutes, status)
                VALUES (:student_id, :user_id, :counselling_type, :topic, :description, :priority, :preferred_date, :preferred_time, :duration_minutes, :status)
            '''), {
                'student_id': student_id, 
                'user_id': user_id, 
                'counselling_type': req_data['type'], 
                'topic': req_data['topic'], 
                'description': req_data['description'], 
                'priority': req_data['priority'], 
                'preferred_date': req_data['date'], 
                'preferred_time': req_data['time'], 
                'duration_minutes': req_data['duration'], 
                'status': req_data['status']
            })
        
        db.session.commit()
        print(f"Created {len(requests_data)} sample counselling requests")

if __name__ == '__main__':
    create_sample_counselling_data()
