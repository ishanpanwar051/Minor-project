"""
College Student Seed Script for EduGuard System
Creates admin, professors, and college students with realistic data
"""

from app import create_app
from models import db, User, Student, Attendance, AcademicRecord, Intervention, RiskProfile, Alert
from datetime import datetime, date, timedelta
import random

def create_admin_user():
    """Create admin user"""
    admin = User.query.filter_by(email='admin@university.edu').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@university.edu',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Created admin user: admin@university.edu / admin123")
    else:
        print("ℹ️ Admin user already exists")

def create_professors():
    """Create professor users"""
    professors_data = [
        ('prof_johnson', 'dr.johnson@university.edu', 'Dr. Robert Johnson'),
        ('prof_smith', 'prof.smith@university.edu', 'Prof. Emily Smith'),
        ('prof_williams', 'dr.williams@university.edu', 'Dr. Michael Williams'),
        ('prof_davis', 'prof.davis@university.edu', 'Prof. Sarah Davis')
    ]
    
    for username, email, name in professors_data:
        professor = User.query.filter_by(email=email).first()
        if not professor:
            professor = User(
                username=username,
                email=email,
                role='faculty'
            )
            professor.set_password('prof123')
            db.session.add(professor)
            print(f"✅ Created professor: {email}")
    
    db.session.commit()

def create_college_students():
    """Create college students with diverse programs and years"""
    departments = ['Computer Science', 'Engineering', 'Business Administration', 'Psychology', 'Biology', 'Mathematics']
    programs = ['B.Tech', 'B.Sc', 'B.Com', 'B.A', 'B.E', 'M.Sc']
    
    students_data = [
        # High risk students
        ('CO2021001', 'Alex', 'Thompson', 'alex.thompson@university.edu', 3, 5, 'Computer Science', 'B.Tech', 2.1, 45),
        ('CO2021002', 'Sarah', 'Miller', 'sarah.miller@university.edu', 2, 3, 'Engineering', 'B.E', 1.8, 30),
        ('CO2021003', 'James', 'Wilson', 'james.wilson@university.edu', 4, 7, 'Business Administration', 'B.Com', 2.3, 52),
        
        # Medium risk students
        ('CO2021004', 'Emma', 'Davis', 'emma.davis@university.edu', 2, 3, 'Psychology', 'B.A', 2.8, 68),
        ('CO2021005', 'Michael', 'Brown', 'michael.brown@university.edu', 3, 5, 'Mathematics', 'B.Sc', 2.6, 72),
        ('CO2021006', 'Olivia', 'Jones', 'olivia.jones@university.edu', 1, 2, 'Biology', 'B.Sc', 2.7, 65),
        
        # Low risk students
        ('CO2021007', 'William', 'Garcia', 'william.garcia@university.edu', 2, 4, 'Computer Science', 'B.Tech', 3.7, 92),
        ('CO2021008', 'Sophia', 'Martinez', 'sophia.martinez@university.edu', 3, 6, 'Engineering', 'B.E', 3.8, 88),
        ('CO2021009', 'Daniel', 'Anderson', 'daniel.anderson@university.edu', 1, 1, 'Business Administration', 'B.Com', 3.5, 85),
        ('CO2021010', 'Isabella', 'Taylor', 'isabella.taylor@university.edu', 4, 8, 'Psychology', 'B.A', 3.6, 90),
        
        # Additional diverse students
        ('CO2021011', 'Joseph', 'Thomas', 'joseph.thomas@university.edu', 2, 4, 'Mathematics', 'B.Sc', 3.2, 78),
        ('CO2021012', 'Mia', 'Jackson', 'mia.jackson@university.edu', 3, 5, 'Computer Science', 'B.Tech', 3.1, 74),
        ('CO2021013', 'Ethan', 'White', 'ethan.white@university.edu', 1, 2, 'Biology', 'B.Sc', 3.4, 82),
        ('CO2021014', 'Charlotte', 'Harris', 'charlotte.harris@university.edu', 2, 3, 'Engineering', 'B.E', 3.3, 76),
        ('CO2021015', 'Alexander', 'Martin', 'alexander.martin@university.edu', 4, 7, 'Business Administration', 'B.Com', 3.0, 70),
    ]
    
    created_students = []
    for student_id, first_name, last_name, email, year, semester, department, program, gpa, credits in students_data:
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            student = Student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                year=year,
                semester=semester,
                department=department,
                program=program,
                enrollment_date=date.today() - timedelta(days=random.randint(365, 1460)),  # 1-4 years ago
                gpa=gpa,
                credits_completed=credits
            )
            db.session.add(student)
            created_students.append(student)
            print(f"✅ Created student: {student_id} - {first_name} {last_name} ({department})")
        else:
            created_students.append(student)
    
    db.session.commit()
    return created_students

def create_academic_records(students):
    """Create college academic records with grades and credits"""
    courses = {
        'Computer Science': [
            ('CS101', 'Introduction to Programming', 4),
            ('CS102', 'Data Structures', 4),
            ('CS201', 'Algorithms', 3),
            ('CS202', 'Database Systems', 3),
            ('CS301', 'Software Engineering', 3),
            ('CS302', 'Computer Networks', 3)
        ],
        'Engineering': [
            ('ENG101', 'Engineering Mathematics', 4),
            ('ENG102', 'Physics for Engineers', 4),
            ('ENG201', 'Mechanics', 3),
            ('ENG202', 'Thermodynamics', 3),
            ('ENG301', 'Fluid Mechanics', 3),
            ('ENG302', 'Heat Transfer', 3)
        ],
        'Business Administration': [
            ('BUS101', 'Principles of Management', 3),
            ('BUS102', 'Business Statistics', 3),
            ('BUS201', 'Financial Accounting', 3),
            ('BUS202', 'Marketing Management', 3),
            ('BUS301', 'Strategic Management', 3),
            ('BUS302', 'Business Ethics', 2)
        ],
        'Psychology': [
            ('PSY101', 'Introduction to Psychology', 3),
            ('PSY102', 'Developmental Psychology', 3),
            ('PSY201', 'Social Psychology', 3),
            ('PSY202', 'Cognitive Psychology', 3),
            ('PSY301', 'Abnormal Psychology', 3),
            ('PSY302', 'Counseling Techniques', 3)
        ],
        'Biology': [
            ('BIO101', 'General Biology', 4),
            ('BIO102', 'Cell Biology', 4),
            ('BIO201', 'Genetics', 3),
            ('BIO202', 'Molecular Biology', 3),
            ('BIO301', 'Ecology', 3),
            ('BIO302', 'Biotechnology', 3)
        ],
        'Mathematics': [
            ('MATH101', 'Calculus I', 4),
            ('MATH102', 'Calculus II', 4),
            ('MATH201', 'Linear Algebra', 3),
            ('MATH202', 'Differential Equations', 3),
            ('MATH301', 'Probability & Statistics', 3),
            ('MATH302', 'Numerical Methods', 3)
        ]
    }
    
    grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F']
    
    for student in students:
        if student.department not in courses:
            continue
            
        dept_courses = courses[student.department]
        student_gpa = student.gpa
        
        # Generate grades based on student's GPA
        for course_code, course_name, credits in dept_courses:
            # Determine grade based on student's GPA with some variation
            if student_gpa >= 3.7:
                grade_weights = [0.4, 0.3, 0.2, 0.1]  # Mostly A's
            elif student_gpa >= 3.3:
                grade_weights = [0.2, 0.3, 0.3, 0.2]  # Mix of A's and B's
            elif student_gpa >= 2.7:
                grade_weights = [0.1, 0.2, 0.4, 0.3]  # Mostly B's
            elif student_gpa >= 2.0:
                grade_weights = [0.05, 0.1, 0.3, 0.55]  # B's and C's
            else:
                grade_weights = [0.02, 0.03, 0.15, 0.8]  # Mostly C's and D's/F's
            
            # Select grade based on weights
            if student_gpa >= 3.7:
                grade = random.choices(['A', 'A-', 'B+', 'B'], weights=[0.4, 0.3, 0.2, 0.1])[0]
            elif student_gpa >= 3.3:
                grade = random.choices(['A-', 'B+', 'B', 'B-'], weights=[0.2, 0.3, 0.3, 0.2])[0]
            elif student_gpa >= 2.7:
                grade = random.choices(['B+', 'B', 'B-', 'C+'], weights=[0.1, 0.2, 0.4, 0.3])[0]
            elif student_gpa >= 2.0:
                grade = random.choices(['B', 'B-', 'C+', 'C'], weights=[0.05, 0.1, 0.3, 0.55])[0]
            else:
                grade = random.choices(['C', 'C-', 'D+', 'D', 'F'], weights=[0.05, 0.1, 0.15, 0.4, 0.3])[0]
            
            # Check if record already exists
            existing = AcademicRecord.query.filter_by(
                student_id=student.id,
                course_code=course_code,
                semester=student.semester
            ).first()
            
            if not existing:
                academic = AcademicRecord(
                    student_id=student.id,
                    course_code=course_code,
                    course_name=course_name,
                    credits=credits,
                    grade=grade,
                    grade_points=0.0,  # Will be calculated
                    semester=student.semester,
                    academic_year='2023-2024',
                    exam_date=date.today() - timedelta(days=random.randint(1, 120))
                )
                academic.grade_points = academic.calculate_grade_points()
                db.session.add(academic)
    
    db.session.commit()
    print("✅ Created academic records")

def create_attendance_records(students):
    """Create attendance records for college lectures"""
    # College students typically have 15-20 hours per week
    subjects_per_week = 5
    
    for student in students:
        attendance_rate = 85.0 if student.gpa >= 3.0 else 75.0 if student.gpa >= 2.0 else 65.0
        
        for day in range(60):  # Last 60 days
            attendance_date = date.today() - timedelta(days=day)
            
            # Create attendance for each subject (assuming 5 subjects per week)
            for subject_num in range(subjects_per_week):
                # Determine attendance status based on student's GPA and attendance rate
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
                    date=attendance_date
                ).first()
                
                if not existing:
                    attendance = Attendance(
                        student_id=student.id,
                        date=attendance_date,
                        status=status,
                        subject=f'Lecture {subject_num + 1}',
                        notes=f'Attendance for Lecture {subject_num + 1}' if status != 'Present' else None
                    )
                    db.session.add(attendance)
    
    db.session.commit()
    print("✅ Created attendance records")

def create_interventions(students):
    """Create college-appropriate interventions"""
    intervention_types = [
        'Academic Counseling', 'Mental Health Support', 'Tutoring Services',
        'Financial Aid Consultation', 'Career Guidance', 'Academic Probation Meeting',
        'Study Skills Workshop', 'Time Management Counseling'
    ]
    
    for student in students:
        # Create interventions based on GPA
        if student.gpa < 2.0:  # High risk - more interventions
            num_interventions = random.randint(3, 6)
        elif student.gpa < 2.7:  # Medium risk - some interventions
            num_interventions = random.randint(1, 3)
        else:  # Low risk - few interventions
            num_interventions = random.randint(0, 2)
        
        for i in range(num_interventions):
            intervention_date = date.today() - timedelta(days=random.randint(1, 90))
            
            intervention = Intervention(
                student_id=student.id,
                date=intervention_date,
                type=random.choice(intervention_types),
                status=random.choice(['Open', 'In Progress', 'Resolved']),
                notes=f'{random.choice(intervention_types)} for {student.full_name()}',
                assigned_to=random.choice(['Dr. Johnson', 'Prof. Smith', 'Counselor Williams', 'Advisor Brown']),
                follow_up_date=intervention_date + timedelta(days=random.randint(7, 30)),
                outcome=random.choice(['Improved academic performance', 'Better time management', 'Increased motivation', 'Ongoing support needed'])
            )
            db.session.add(intervention)
    
    db.session.commit()
    print("✅ Created intervention records")

def create_risk_profiles(students):
    """Create risk profiles for college students"""
    for student in students:
        # Check if risk profile already exists
        existing = RiskProfile.query.filter_by(student_id=student.id).first()
        if existing:
            continue
        
        # Calculate risk factors based on college student metrics
        attendance_records = Attendance.query.filter_by(student_id=student.id).all()
        academic_records = AcademicRecord.query.filter_by(student_id=student.id).all()
        
        # Calculate attendance rate
        total_classes = len(attendance_records)
        present_classes = len([a for a in attendance_records if a.status == 'Present'])
        attendance_rate = (present_classes / total_classes * 100) if total_classes > 0 else 85.0
        
        # Use GPA as primary academic factor
        gpa_factor = max(0, (4.0 - student.gpa) * 25)  # Convert GPA to 0-100 scale
        
        # Calculate risk factors
        attendance_factor = max(0, (100 - attendance_rate) * 0.3)  # 30% weight
        academic_factor = gpa_factor * 0.5  # 50% weight (GPA is crucial)
        engagement_factor = random.uniform(0, 15)  # 15% weight
        demographic_factor = random.uniform(0, 5)  # 5% weight
        
        # Calculate total risk score
        risk_score = attendance_factor + academic_factor + engagement_factor + demographic_factor
        
        # Determine risk level
        if risk_score >= 75:
            risk_level = 'Critical'
        elif risk_score >= 55:
            risk_level = 'High'
        elif risk_score >= 35:
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
        
        # Count failing courses (grades below C)
        failing_courses = len([ar for ar in academic_records if ar.grade in ['D+', 'D', 'F']])
        
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
            average_score=student.gpa * 25,  # Convert GPA to 0-100 scale
            engagement_score=random.uniform(40, 90),
            consecutive_absences=consecutive_absences,
            failing_subjects=failing_courses,
            intervention_history=intervention_history
        )
        
        db.session.add(risk_profile)
        print(f"✅ Created risk profile for {student.student_id} - {risk_level} risk (GPA: {student.gpa})")
    
    db.session.commit()

def create_alerts(students):
    """Create alerts for at-risk college students"""
    alert_types = ['Academic Performance', 'Attendance', 'Mental Health', 'Financial Aid', 'Registration']
    
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
                severity=risk_profile.risk_level if risk_profile.risk_level in ['Critical', 'High', 'Medium'] else 'Low',
                title=f'{random.choice(alert_types)} Alert for {student.student_id}',
                description=f'Alert regarding {random.choice(alert_types).lower()} performance for {student.full_name()} in {student.department}',
                status=random.choice(['Active', 'Resolved']),
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(alert)
    
    db.session.commit()
    print("✅ Created alerts")

def main():
    """Main function to seed the college database"""
    app = create_app()
    
    with app.app_context():
        print("🎓 Starting college database seeding...")
        
        # Clear existing data
        print("🗑️  Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create data
        create_admin_user()
        create_professors()
        students = create_college_students()
        create_academic_records(students)
        create_attendance_records(students)
        create_interventions(students)
        create_risk_profiles(students)
        create_alerts(students)
        
        # Print summary
        print("\n📊 College Database Summary:")
        print(f"  Users: {User.query.count()}")
        print(f"  Students: {Student.query.count()}")
        print(f"  Attendance Records: {Attendance.query.count()}")
        print(f"  Academic Records: {AcademicRecord.query.count()}")
        print(f"  Interventions: {Intervention.query.count()}")
        print(f"  Risk Profiles: {RiskProfile.query.count()}")
        print(f"  Alerts: {Alert.query.count()}")
        
        # Department breakdown
        print("\n🏛️ Department Breakdown:")
        departments = db.session.query(Student.department, db.func.count(Student.id)).group_by(Student.department).all()
        for dept, count in departments:
            print(f"  {dept}: {count} students")
        
        print("\n🎉 College database seeding completed successfully!")
        print("\n🔑 Login Credentials:")
        print("  Admin: admin@university.edu / admin123")
        print("  Professors: dr.johnson@university.edu / prof123")
        print("             prof.smith@university.edu / prof123")
        print("             dr.williams@university.edu / prof123")
        print("             prof.davis@university.edu / prof123")

if __name__ == '__main__':
    main()
