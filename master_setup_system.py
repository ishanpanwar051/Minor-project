"""
Master Setup System for EduGuard
Populates the entire database with comprehensive, high-quality sample data.
"""

from app import create_app
from models import (
    db, User, Student, Scholarship, ScholarshipApplication, 
    ScholarshipStatus, ApplicationStatus, CounsellingRequest, 
    CounsellingStatus, AIInteraction, AnalyticsData, RiskProfile, 
    Attendance, Alert, Notification
)
from models_support import StudentGoal, MoodLog
from datetime import datetime, timedelta, date
import json
import random

def seed_everything():
    app = create_app()
    with app.app_context():
        print("🚀 Starting Master Data Seeding...")
        
        # 2. Create/Update Users & Students
        users_data = [
            ('john_doe', 'john.doe@eduguard.edu', 'student', 'student123', 'John', 'Doe', 'Computer Science', 3.8, 4),
            ('rohit_v', 'rohit.verma@eduguard.edu', 'student', 'student123', 'Rohit', 'Verma', 'Mechanical Engineering', 3.2, 3),
            ('jane_s', 'jane.smith@eduguard.edu', 'student', 'student123', 'Jane', 'Smith', 'Data Science', 3.9, 4),
            ('alex_b', 'alex.brown@eduguard.edu', 'student', 'student123', 'Alex', 'Brown', 'Civil Engineering', 2.8, 2),
        ]
        
        students_objs = []
        for username, email, role, pwd, f_name, l_name, dept, gpa, year in users_data:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(username=username, email=email, role=role)
                user.set_password(pwd)
                db.session.add(user)
                db.session.flush()
            
            student = Student.query.filter_by(user_id=user.id).first()
            if not student:
                student = Student(
                    user_id=user.id,
                    student_id=f"STU{random.randint(1000, 9999)}",
                    first_name=f_name,
                    last_name=l_name,
                    email=email,
                    department=dept,
                    year=year,
                    semester=1,
                    gpa=gpa,
                    enrollment_date=date(2022, 9, 1),
                    credits_completed=year * 30,
                    annual_income=random.randint(15000, 60000),
                    financial_need_level='High' if gpa < 3.0 or random.random() > 0.7 else 'Medium'
                )
                db.session.add(student)
                db.session.flush()
            students_objs.append(student)
        
        db.session.commit()
        print(f"✅ Seeded {len(students_objs)} students")

        # 3. Seed Scholarships
        titles = [
            ('Global Excellence Scholarship', 10000.0, 3.7, 'High'),
            ('STEM Innovation Award', 5000.0, 3.5, 'Medium'),
            ('Future Leaders Grant', 3000.0, 3.2, 'Any'),
            ('EduGuard Hardship Support', 4500.0, 2.5, 'Critical'),
            ('Women in Tech Foundation', 6000.0, 3.4, 'Medium'),
            ('Sustainability Research Grant', 2500.0, 3.0, 'Any'),
            ('Campus Merit Award', 1500.0, 3.8, 'Any'),
            ('Diversity in Engineering', 4000.0, 3.1, 'High')
        ]
        
        scholarship_objs = []
        for title, amt, gpa_req, priority in titles:
            existing = Scholarship.query.filter_by(title=title).first()
            if not existing:
                s = Scholarship(
                    title=title,
                    description=f"This prestigious award recognises outstanding students with {priority} potential. Recipients receive financial support to pursue academic excellence and contribute to their field of study.",
                    provider="EduGuard Global Foundation",
                    amount=amt,
                    currency="USD",
                    min_gpa=gpa_req,
                    application_deadline=datetime.utcnow() + timedelta(days=random.randint(15, 90)),
                    status=ScholarshipStatus.ACTIVE,
                    ai_tags=json.dumps(['AI', 'Data', 'Leadership']),
                    departments=json.dumps(['Computer Science', 'Data Science', 'Engineering', 'Mechanical Engineering', 'Civil Engineering'])
                )
                db.session.add(s)
                db.session.flush()
                scholarship_objs.append(s)
            else:
                scholarship_objs.append(existing)
        
        db.session.commit()
        print(f"✅ Seeded {len(scholarship_objs)} scholarships")

        # 4. Seed Applications
        print("📋 Seeding scholarship applications...")
        for student in students_objs:
            potential_scholarships = random.sample(scholarship_objs, min(3, len(scholarship_objs)))
            for i, s in enumerate(potential_scholarships):
                existing_app = ScholarshipApplication.query.filter_by(student_id=student.id, scholarship_id=s.id).first()
                if not existing_app:
                    status = [ApplicationStatus.PENDING, ApplicationStatus.APPROVED, ApplicationStatus.UNDER_REVIEW][i % 3]
                    app_obj = ScholarshipApplication(
                        scholarship_id=s.id,
                        student_id=student.id,
                        status=status,
                        application_date=datetime.utcnow() - timedelta(days=random.randint(1, 45)),
                        personal_statement="I am passionate about my field of study and this scholarship will help me achieve my academic goals while contributing to research and innovation.",
                        ai_eligibility_score=random.uniform(70, 95),
                        ai_success_probability=random.uniform(0.4, 0.9),
                        gpa_at_application=student.gpa
                    )
                    db.session.add(app_obj)
        
        db.session.commit()

        # 5. Seed Counselling Requests
        print("🤝 Seeding counselling requests...")
        counselling_topics = [
            ("Career Guidance", "I need help identifying the best career paths in my field and what skills to develop.", "career"),
            ("Academic Stress", "I have been feeling overwhelmed with coursework and need strategies to manage my workload.", "personal"),
            ("Scholarship Documentation", "I need guidance on preparing strong scholarship applications and personal statements.", "academic"),
            ("Internship Search", "I am looking for internship opportunities and need help with my resume and interview prep.", "career"),
            ("Time Management", "I struggle with balancing studies, extracurriculars, and personal life.", "academic"),
            ("Mental Health Support", "I have been experiencing anxiety and would like to talk to someone about coping strategies.", "personal"),
        ]
        for student in students_objs:
            count = random.randint(2, 3)
            for j in range(count):
                topic, desc, c_type = random.choice(counselling_topics)
                existing = CounsellingRequest.query.filter_by(
                    student_id=student.id, topic=topic
                ).first()
                if not existing:
                    c_req = CounsellingRequest(
                        student_id=student.id,
                        user_id=student.user_id,
                        topic=topic,
                        description=desc,
                        counselling_type=c_type,
                        status=random.choice([CounsellingStatus.REQUESTED, CounsellingStatus.SCHEDULED, CounsellingStatus.COMPLETED]),
                        request_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                        priority=random.choice(['low', 'medium', 'high'])
                    )
                    db.session.add(c_req)
        db.session.commit()

        # 6. Seed Attendance & Risk Profiles
        print("📈 Seeding attendance and risk profiles...")
        for student in students_objs:
            # Check if attendance already exists
            existing_att = Attendance.query.filter_by(student_id=student.id).count()
            if existing_att < 10:
                for k in range(60):
                    att_date = date.today() - timedelta(days=k)
                    if att_date.weekday() < 5:
                        db.session.add(Attendance(
                            student_id=student.id,
                            date=att_date,
                            status='Present' if random.random() > 0.12 else 'Absent',
                            course=f'CS{random.randint(100, 400)}'
                        ))
            
            risk = RiskProfile.query.filter_by(student_id=student.id).first()
            if not risk:
                risk = RiskProfile(
                    student_id=student.id,
                    attendance_rate=random.uniform(75, 95),
                    academic_performance=student.gpa * 10 if student.gpa else 70,
                    risk_level='Low' if (student.gpa or 0) > 3.0 else 'Medium',
                    financial_issues=random.choice([True, False]),
                    family_problems=random.choice([True, False, False]),
                    mental_wellbeing_score=random.randint(6, 10)
                )
                risk._rule_based_calculation()
                db.session.add(risk)
        
        # Global Analytics
        for l in range(30):
            analytic = AnalyticsData(
                date=date.today() - timedelta(days=l),
                metric_type='platform_engagement',
                metric_name='active_users',
                metric_value=float(random.randint(10, 50)),
                ai_trend_direction='up'
            )
            db.session.add(analytic)

        db.session.commit()
        
        # 7. Seed AI Interaction Logs
        print("🤖 Seeding AI interactions...")
        bot_queries = [
            "What are the best scholarships for me?",
            "How can I improve my GPA?",
            "Show my application status",
            "Give me career advice",
            "When is the STEM grant deadline?"
        ]
        for student in students_objs:
            for m in range(2):
                db.session.add(AIInteraction(
                    user_id=student.user_id,
                    session_id=f"session_{student.id}_{m}",
                    interaction_type='query',
                    user_query=random.choice(bot_queries),
                    ai_response="I have analyzed your profile and found several matching opportunities. Check your dashboard for details.",
                    intent_classification='scholarship_query',
                    confidence_score=0.95
                ))
        db.session.commit()

        # 8. Seed Student Goals
        print("🎯 Seeding student goals...")
        goal_templates = [
            ("Achieve GPA above 3.5", "Focus on core subjects and attend all lectures to improve overall GPA", 30, 65),
            ("Complete capstone project", "Finish the research paper and build the working prototype", 60, 40),
            ("Get an internship", "Apply to at least 10 companies and prepare for technical interviews", 45, 20),
            ("Learn Python for Data Science", "Complete the online course and build 3 portfolio projects", 50, 80),
            ("Improve public speaking", "Join the debate club and present in at least 2 seminars", 40, 50),
            ("Read 5 technical books this semester", "Cover topics in algorithms, system design, and machine learning", 90, 30),
            ("Build personal portfolio website", "Design and develop a professional portfolio to showcase projects", 20, 90),
            ("Apply for 3 scholarships", "Research eligibility, prepare documents and submit applications", 25, 70),
        ]
        for student in students_objs:
            existing_goals = StudentGoal.query.filter_by(student_id=student.id).count()
            if existing_goals < 3:
                selected = random.sample(goal_templates, min(4, len(goal_templates)))
                for title, desc, days_offset, progress in selected:
                    status = 'Active'
                    if progress >= 100:
                        status = 'Completed'
                    goal = StudentGoal(
                        student_id=student.id,
                        title=title,
                        description=desc,
                        target_date=date.today() + timedelta(days=days_offset),
                        progress=progress,
                        status=status,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(5, 30))
                    )
                    db.session.add(goal)
        db.session.commit()
        print("✅ Seeded student goals")

        # 9. Seed Mood Logs
        print("😊 Seeding mood logs...")
        mood_notes = [
            "Feeling productive today!",
            "A bit stressed about the upcoming exam.",
            "Great day! Finished my assignment early.",
            "Feeling neutral, just a regular day.",
            "Feeling tired but pushing through.",
            "Happy after getting good feedback on my project.",
            "A bit anxious about internship interviews.",
            "Relaxed weekend vibes.",
            "Motivated after the counselling session.",
            "Feeling overwhelmed with deadlines."
        ]
        for student in students_objs:
            existing_moods = MoodLog.query.filter_by(student_id=student.id).count()
            if existing_moods < 5:
                for k in range(14):
                    log_date = date.today() - timedelta(days=k)
                    # Skip some days randomly
                    if random.random() > 0.3:
                        existing = MoodLog.query.filter_by(student_id=student.id, log_date=log_date).first()
                        if not existing:
                            mood = MoodLog(
                                student_id=student.id,
                                mood_score=random.randint(2, 5),
                                note=random.choice(mood_notes),
                                log_date=log_date,
                                logged_at=datetime.utcnow() - timedelta(days=k, hours=random.randint(8, 18))
                            )
                            db.session.add(mood)
        db.session.commit()
        print("✅ Seeded mood logs")

        # 10. Seed Alerts and Notifications
        print("🔔 Seeding alerts and notifications...")
        for student in students_objs:
            # Seed Notifications
            for i in range(3):
                notification = Notification(
                    user_id=student.user_id,
                    title=random.choice(["Scholarship Match Found!", "New Deadline Approaching", "Counselling Appointment Confirmed", "Profile Update Required"]),
                    message="You have a new update regarding your academic journey. Please review your dashboard for details.",
                    notification_type=random.choice(["scholarship", "system", "counselling", "academic"]),
                    is_read=random.choice([True, False]),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 5))
                )
                db.session.add(notification)
            
            # Seed Alerts
            if student.gpa and student.gpa < 3.0:
                alert = Alert(
                    student_id=student.id,
                    alert_type="academic_warning",
                    severity="High",
                    title="GPA Alert",
                    description=f"Your GPA has dropped to {student.gpa}. Consider scheduling a counselling session.",
                    status="Active",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 3))
                )
                db.session.add(alert)
        db.session.commit()
        print("✅ Seeded alerts and notifications")

        print("\n✨ Master Seeding Complete! System is fully populated.")
        print("=" * 50)
        print("🔐 LOGIN CREDENTIALS:")
        print("STUDENT: john.doe@eduguard.edu / student123")
        print("ADMIN:   admin@eduguard.edu / admin123")
        print("=" * 50)

if __name__ == "__main__":
    seed_everything()
