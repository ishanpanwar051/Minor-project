from faker import Faker
from app import create_app, db
from models import User, Student, Attendance, AcademicRecord, Intervention, RiskProfile
from utils import update_student_risk
from datetime import datetime, timedelta
import random

fake = Faker()
app = create_app()

def seed_database():
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        print("Creating Admin User...")
        admin = User(username='admin', email='admin@school.edu', password_hash='password', role='admin')
        db.session.add(admin)
        
        print("Creating Students...")
        students = []
        for i in range(50):
            student = Student(
                student_id=f"STD{2024000 + i}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number(),
                grade_level=random.randint(9, 12),
                enrollment_date=fake.date_between(start_date='-2y', end_date='-1y')
            )
            students.append(student)
            db.session.add(student)
        
        db.session.commit()
        
        print("Generating Attendance & Academic Records...")
        subjects = ['Math', 'Science', 'English', 'History', 'CS']
        
        for student in students:
            # Simulate different profiles:
            # 1. Good Student (High Att, High Grades)
            # 2. At Risk Student (Low Att OR Low Grades)
            # 3. Dropout Risk (Low Att AND Low Grades)
            
            profile_type = random.choices(['good', 'average', 'risk', 'critical'], weights=[40, 30, 20, 10])[0]
            
            # Attendance
            for day in range(30):
                date = datetime.now() - timedelta(days=30-day)
                if date.weekday() >= 5: continue # Skip weekends
                
                if profile_type == 'good':
                    status = random.choices(['Present', 'Late', 'Absent'], weights=[95, 3, 2])[0]
                elif profile_type == 'average':
                    status = random.choices(['Present', 'Late', 'Absent'], weights=[85, 10, 5])[0]
                elif profile_type == 'risk':
                    status = random.choices(['Present', 'Late', 'Absent'], weights=[60, 10, 30])[0]
                else: # critical
                    status = random.choices(['Present', 'Late', 'Absent'], weights=[40, 10, 50])[0]
                
                att = Attendance(student_id=student.id, date=date, status=status)
                db.session.add(att)
                
            # Academics
            for subject in subjects:
                if profile_type == 'good':
                    score = random.uniform(80, 100)
                elif profile_type == 'average':
                    score = random.uniform(60, 85)
                elif profile_type == 'risk':
                    score = random.uniform(40, 65)
                else:
                    score = random.uniform(20, 50)
                    
                record = AcademicRecord(
                    student_id=student.id,
                    subject=subject,
                    score=round(score, 1),
                    max_score=100,
                    exam_type='Midterm',
                    date=datetime.now() - timedelta(days=random.randint(10, 60))
                )
                db.session.add(record)
                
            db.session.commit()
            
            # Calculate Risk
            update_student_risk(student)
            
            # Add some interventions for risky students
            if profile_type in ['risk', 'critical']:
                if random.random() > 0.5:
                    intervention = Intervention(
                        student_id=student.id,
                        type=random.choice(['Counseling', 'Parent Meeting']),
                        notes=fake.sentence(),
                        date=datetime.now() - timedelta(days=random.randint(1, 10))
                    )
                    db.session.add(intervention)
                    
        db.session.commit()
        print("Database Seeded Successfully!")

if __name__ == '__main__':
    seed_database()
