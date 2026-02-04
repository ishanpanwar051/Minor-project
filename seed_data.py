"""
Comprehensive Seed Script for EduGuard System
Creates admin, teachers, students, attendance, academic records, interventions, and risk profiles
"""

from app import create_app
from models import db, User, Student, Attendance, AcademicRecord, Intervention, RiskProfile, Alert
from datetime import datetime, date, timedelta
import random

def create_admin_user():
    """Create admin user"""
    admin = User.query.filter_by(email='admin@school.edu').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@school.edu',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Created admin user: admin@school.edu / admin123")
    else:
        print("ℹ️ Admin user already exists")

def create_teachers():
    """Create teacher users"""
    teachers_data = [
        ('john_teacher', 'john.smith@school.edu', 'John Smith'),
        ('sarah_teacher', 'sarah.jones@school.edu', 'Sarah Jones'),
        ('mike_teacher', 'mike.wilson@school.edu', 'Mike Wilson')
    ]
    
    for username, email, name in teachers_data:
        teacher = User.query.filter_by(email=email).first()
        if not teacher:
            teacher = User(
                username=username,
                email=email,
                role='faculty'
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            print(f"✅ Created teacher: {email}")
    
    db.session.commit()

def create_sample_students():
    """Create sample students with diverse risk profiles"""
    students_data = [
        # High risk students
        ('ST1001', 'Alice', 'Johnson', 'alice.j@student.edu', 3, 85.0, 45.0, 12),
        ('ST1002', 'Bob', 'Smith', 'bob.smith@student.edu', 3, 70.0, 52.0, 8),
        ('ST1003', 'Charlie', 'Brown', 'charlie.brown@student.edu', 4, 60.0, 48.0, 15),
        
        # Medium risk students
        ('ST1004', 'Diana', 'Prince', 'diana.prince@student.edu', 2, 88.0, 72.0, 4),
        ('ST1005', 'Eve', 'Adams', 'eve.adams@student.edu', 3, 82.0, 68.0, 3),
        ('ST1006', 'Frank', 'Miller', 'frank.miller@student.edu', 4, 90.0, 65.0, 5),
        
        # Low risk students
        ('ST1007', 'Grace', 'Lee', 'grace.lee@student.edu', 2, 95.0, 92.0, 0),
        ('ST1008', 'Henry', 'Ford', 'henry.ford@student.edu', 3, 98.0, 88.0, 1),
        ('ST1009', 'Ivy', 'Chen', 'ivy.chen@student.edu', 4, 96.0, 85.0, 0),
        ('ST1010', 'Jack', 'Davis', 'jack.davis@student.edu', 2, 94.0, 90.0, 2),
        
        # Additional diverse students
        ('ST1011', 'Karen', 'White', 'karen.white@student.edu', 3, 75.0, 70.0, 6),
        ('ST1012', 'Leo', 'Martinez', 'leo.martinez@student.edu', 4, 80.0, 75.0, 4),
        ('ST1013', 'Mia', 'Taylor', 'mia.taylor@student.edu', 2, 92.0, 82.0, 2),
        ('ST1014', 'Noah', 'Anderson', 'noah.anderson@student.edu', 3, 87.0, 78.0, 3),
        ('ST1015', 'Olivia', 'Thomas', 'olivia.thomas@student.edu', 4, 91.0, 84.0, 1),
    ]
    
    created_students = []
    for student_id, first_name, last_name, email, semester, attendance_rate, avg_score, absences in students_data:
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            student = Student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                semester=semester,
                enrollment_date=date.today() - timedelta(days=random.randint(30, 365))
            )
            db.session.add(student)
            created_students.append(student)
            print(f"✅ Created student: {student_id} - {first_name} {last_name}")
        else:
            created_students.append(student)
    
    db.session.commit()
    return created_students

def create_attendance_records(students):
    """Create attendance records for the past 30 days"""
    subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'History', 'Computer Science']
    statuses = ['Present', 'Absent', 'Late', 'Excused']
    
    for student in students:
        # Create attendance based on student's attendance rate
        attendance_rate = getattr(student, 'attendance_rate', 85.0)
        
        for day in range(30):
            attendance_date = date.today() - timedelta(days=day)
            
            for subject in subjects:
                # Determine attendance status based on student's attendance rate
                rand = random.random() * 100
                if rand < attendance_rate:
                    status = 'Present'
                elif rand < attendance_rate + 5:
                    status = 'Late'
                elif rand < attendance_rate + 10:
                    status = 'Excused'
                else:
                    status = 'Absent'
                
                # Check if record already exists
                existing = Attendance.query.filter_by(
                    student_id=student.id,
                    date=attendance_date,
                    subject=subject
                ).first()
                
                if not existing:
                    attendance = Attendance(
                        student_id=student.id,
                        date=attendance_date,
                        status=status,
                        subject=subject,
                        notes=f'Attendance for {subject}' if status != 'Present' else None
                    )
                    db.session.add(attendance)
    
    db.session.commit()
    print("✅ Created attendance records")

def create_academic_records(students):
    """Create academic records for students"""
    subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'History', 'Computer Science']
    exam_types = ['Midterm', 'Final', 'Quiz', 'Assignment']
    
    for student in students:
        avg_score = getattr(student, 'average_score', 75.0)
        
        for subject in subjects:
            for exam_type in exam_types:
                # Generate score based on student's average with some variation
                score = max(0, min(100, avg_score + random.uniform(-20, 20)))
                max_score = 100.0
                
                # Adjust for exam type
                if exam_type == 'Quiz':
                    max_score = 50.0
                    score = score * 0.5
                elif exam_type == 'Assignment':
                    max_score = 25.0
                    score = score * 0.25
                
                # Check if record already exists
                existing = AcademicRecord.query.filter_by(
                    student_id=student.id,
                    subject=subject,
                    exam_type=exam_type
                ).first()
                
                if not existing:
                    academic = AcademicRecord(
                        student_id=student.id,
                        subject=subject,
                        score=score,
                        max_score=max_score,
                        exam_type=exam_type,
                        exam_date=date.today() - timedelta(days=random.randint(1, 90)),
                        semester=student.semester,
                        notes=f'Performance in {subject} {exam_type}'
                    )
                    db.session.add(academic)
    
    db.session.commit()
    print("✅ Created academic records")

def create_interventions(students):
    """Create intervention records for at-risk students"""
    intervention_types = ['Counseling', 'Parent Meeting', 'Remedial Class', 'Academic Support', 'Mentoring']
    statuses = ['Open', 'In Progress', 'Resolved', 'Cancelled']
    
    for student in students:
        # Create interventions based on risk level
        # Use a temporary risk score since risk profiles aren't created yet
        temp_risk_score = random.uniform(0, 100)
        
        if temp_risk_score > 60:  # High risk - more interventions
            num_interventions = random.randint(2, 5)
        elif temp_risk_score > 40:  # Medium risk - some interventions
            num_interventions = random.randint(1, 3)
        else:  # Low risk - few or no interventions
            num_interventions = random.randint(0, 2)
        
        for i in range(num_interventions):
            intervention_date = date.today() - timedelta(days=random.randint(1, 60))
            
            intervention = Intervention(
                student_id=student.id,
                date=intervention_date,
                type=random.choice(intervention_types),
                status=random.choice(statuses),
                notes=f'Intervention for {student.full_name()} - {random.choice(intervention_types)}',
                assigned_to=random.choice(['Dr. Smith', 'Ms. Johnson', 'Mr. Williams', 'Counselor Brown']),
                follow_up_date=intervention_date + timedelta(days=random.randint(7, 30)),
                outcome=random.choice(['Improved attendance', 'Better grades', 'Ongoing support', 'Completed successfully'])
            )
            db.session.add(intervention)
    
    db.session.commit()
    print("✅ Created intervention records")

def create_risk_profiles(students):
    """Create risk profiles for students"""
    for student in students:
        # Check if risk profile already exists
        existing = RiskProfile.query.filter_by(student_id=student.id).first()
        if existing:
            continue
        
        # Calculate risk factors based on attendance and academic performance
        attendance_records = Attendance.query.filter_by(student_id=student.id).all()
        academic_records = AcademicRecord.query.filter_by(student_id=student.id).all()
        
        # Calculate attendance rate
        total_classes = len(attendance_records)
        present_classes = len([a for a in attendance_records if a.status == 'Present'])
        attendance_rate = (present_classes / total_classes * 100) if total_classes > 0 else 85.0
        
        # Calculate average score
        if academic_records:
            total_percentage = sum([ar.percentage() for ar in academic_records])
            avg_score = total_percentage / len(academic_records)
        else:
            avg_score = 75.0
        
        # Calculate risk factors
        attendance_factor = max(0, (100 - attendance_rate) * 0.4)  # 40% weight
        academic_factor = max(0, (100 - avg_score) * 0.3)  # 30% weight
        engagement_factor = random.uniform(0, 20)  # 20% weight (simulated)
        demographic_factor = random.uniform(0, 10)  # 10% weight (simulated)
        
        # Calculate total risk score
        risk_score = attendance_factor + academic_factor + engagement_factor + demographic_factor
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = 'Critical'
        elif risk_score >= 60:
            risk_level = 'High'
        elif risk_score >= 40:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Count consecutive absences
        consecutive_absences = 0
        sorted_attendance = sorted(attendance_records, key=lambda x: x.date, reverse=True)
        for record in sorted_attendance:
            if record.status in ['Absent', 'Late']:
                consecutive_absences += 1
            else:
                break
        
        # Count failing subjects
        failing_subjects = 0
        subject_scores = {}
        for ar in academic_records:
            if ar.subject not in subject_scores:
                subject_scores[ar.subject] = []
            subject_scores[ar.subject].append(ar.percentage())
        
        for subject, scores in subject_scores.items():
            avg_subject_score = sum(scores) / len(scores)
            if avg_subject_score < 60:
                failing_subjects += 1
        
        # Count intervention history
        intervention_history = Intervention.query.filter_by(student_id=student.id).count()
        
        risk_profile = RiskProfile(
            student_id=student.id,
            risk_score=min(100, risk_score),
            risk_level=risk_level,
            attendance_factor=attendance_factor,
            academic_factor=academic_factor,
            engagement_factor=engagement_factor,
            demographic_factor=demographic_factor,
            attendance_rate=attendance_rate,
            average_score=avg_score,
            engagement_score=random.uniform(30, 90),
            consecutive_absences=consecutive_absences,
            failing_subjects=failing_subjects,
            intervention_history=intervention_history
        )
        
        db.session.add(risk_profile)
        print(f"✅ Created risk profile for {student.student_id} - {risk_level} risk")
    
    db.session.commit()

def create_alerts(students):
    """Create alerts for high-risk students"""
    alert_types = ['Attendance', 'Academic', 'Behavioral', 'Risk']
    severities = ['Low', 'Medium', 'High', 'Critical']
    
    for student in students:
        risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
        if not risk_profile:
            continue
        
        # Create alerts based on risk level
        if risk_profile.risk_level in ['High', 'Critical']:
            num_alerts = random.randint(2, 4)
        elif risk_profile.risk_level == 'Medium':
            num_alerts = random.randint(1, 2)
        else:
            num_alerts = random.randint(0, 1)
        
        for i in range(num_alerts):
            alert = Alert(
                student_id=student.id,
                alert_type=random.choice(alert_types),
                severity=risk_profile.risk_level if risk_profile.risk_level in severities else 'Medium',
                title=f'{random.choice(alert_types)} Alert for {student.student_id}',
                description=f'Alert regarding {random.choice(alert_types).lower()} performance for {student.full_name()}',
                status=random.choice(['Active', 'Resolved']),
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(alert)
    
    db.session.commit()
    print("✅ Created alerts")

def main():
    """Main function to seed the database"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("🗑️  Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create data
        create_admin_user()
        create_teachers()
        students = create_sample_students()
        create_attendance_records(students)
        create_academic_records(students)
        create_interventions(students)
        create_risk_profiles(students)
        create_alerts(students)
        
        # Print summary
        print("\n📊 Database Summary:")
        print(f"  Users: {User.query.count()}")
        print(f"  Students: {Student.query.count()}")
        print(f"  Attendance Records: {Attendance.query.count()}")
        print(f"  Academic Records: {AcademicRecord.query.count()}")
        print(f"  Interventions: {Intervention.query.count()}")
        print(f"  Risk Profiles: {RiskProfile.query.count()}")
        print(f"  Alerts: {Alert.query.count()}")
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n🔑 Login Credentials:")
        print("  Admin: admin@school.edu / admin123")
        print("  Teachers: john.smith@school.edu / teacher123")
        print("           sarah.jones@school.edu / teacher123")
        print("           mike.wilson@school.edu / teacher123")

if __name__ == '__main__':
    main()
