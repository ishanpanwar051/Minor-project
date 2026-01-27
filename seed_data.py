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
        admin = User(username='admin', email='admin@college.edu', role='admin')
        admin.set_password('password')
        db.session.add(admin)

        print("Creating Faculty User...")
        faculty = User(username='faculty', email='faculty@college.edu', role='faculty')
        faculty.set_password('password')
        db.session.add(faculty)
        
        print("Creating Students...")
        students = []
        
        # Create a specific demo student for the user
        demo_student = Student(
            student_id="STD2024999",
            first_name="Ishan",
            last_name="Demo",
            email="ishan@gmail.com",
            phone="123-456-7890",
            semester=6,
            enrollment_date=datetime.now() - timedelta(days=365*2)
        )
        students.append(demo_student)
        db.session.add(demo_student)

        for i in range(49):
            student = Student(
                student_id=f"STD{2024000 + i}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number(),
                semester=random.randint(1, 8),
                enrollment_date=fake.date_between(start_date='-3y', end_date='-1y')
            )
            students.append(student)
            db.session.add(student)
        
        db.session.commit()
        
        print("Generating Attendance & Academic Records...")
        subjects = ['Data Structures', 'Algorithms', 'Database', 'Operating Systems', 'Networks']
        
        # Create User accounts for first 5 students for testing
        print("Creating User accounts for students...")
        # Ensure Ishan has a login
        ishan_user = User(username='ishan_demo', email='ishan@gmail.com', role='student')
        ishan_user.set_password('password')
        db.session.add(ishan_user)
        print("  Created User for Student: Ishan (ishan@gmail.com) / password")

        for i, student in enumerate(students[1:6]):
            user = User(
                username=student.student_id, 
                email=student.email, 
                role='student'
            )
            user.set_password('password')
            db.session.add(user)
            print(f"  Created User for Student: {student.first_name} ({student.email}) / password")

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
