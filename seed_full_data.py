import os
from app import create_app
from models import db, User, Student, Scholarship, ScholarshipApplication, ScholarshipStatus, ApplicationStatus, CounsellingRequest, CounsellingStatus, AIInteraction, AnalyticsData, RiskProfile, Attendance
from datetime import datetime, timedelta, date
import json
import random

def seed_comprehensive_data():
    app = create_app()
    with app.app_context():
        print("🌱 Starting comprehensive data seeding...")
        
        # 1. Ensure students exist (via create_initial_data)
        # We'll target 'john.doe@eduguard.edu'
        john_user = User.query.filter_by(email='john.doe@eduguard.edu').first()
        if not john_user:
            print("❌ John Doe not found. Please run create_initial_data first.")
            return
        
        student = Student.query.filter_by(user_id=john_user.id).first()
        if not student:
            print("❌ Student profile not found for John Doe.")
            return

        # Update John's profile to make him eligible for more things
        student.annual_income = 20000
        student.financial_need_level = 'High'
        student.career_interests = 'Software Engineering, AI, Cloud Computing'
        student.gpa = 3.8
        db.session.commit()

        # 2. Seed Scholarships
        print("🎓 Seeding Scholarships...")
        scholarships = [
            {
                'title': 'Global Tech Merit Scholarship',
                'description': 'Awarded to high-achieving Computer Science students with a focus on innovation.',
                'provider': 'Global Tech Foundation',
                'amount': 5000.0,
                'min_gpa': 3.5,
                'departments': json.dumps(['Computer Science', 'Engineering']),
                'year_level': 'Sophomore',
                'application_deadline': datetime.utcnow() + timedelta(days=30),
                'status': ScholarshipStatus.ACTIVE,
                'ai_tags': json.dumps(['Software', 'AI', 'Technology'])
            },
            {
                'title': 'Opportunity Financial Grant',
                'description': 'Need-based grant for students facing financial hardships.',
                'provider': 'EduSupport Org',
                'amount': 3000.0,
                'max_income': 30000.0,
                'application_deadline': datetime.utcnow() + timedelta(days=15),
                'status': ScholarshipStatus.ACTIVE,
                'ai_tags': json.dumps(['Financial Aid', 'Support'])
            },
            {
                'title': 'STEM Leadership Award',
                'description': 'Recognizing leadership qualities in STEM fields.',
                'provider': 'STEM Council',
                'amount': 2500.0,
                'min_gpa': 3.2,
                'departments': json.dumps(['Engineering', 'Science', 'Computer Science']),
                'application_deadline': datetime.utcnow() + timedelta(days=45),
                'status': ScholarshipStatus.ACTIVE,
                'ai_tags': json.dumps(['Leadership', 'STEM'])
            }
        ]

        for s_data in scholarships:
            existing = Scholarship.query.filter_by(title=s_data['title']).first()
            if not existing:
                s = Scholarship(**s_data)
                db.session.add(s)
        
        db.session.commit()

        # 3. Seed Scholarship Applications for John
        print("📝 Seeding Applications...")
        active_scholarships = Scholarship.query.all()
        for i, s in enumerate(active_scholarships):
            existing_app = ScholarshipApplication.query.filter_by(student_id=student.id, scholarship_id=s.id).first()
            if not existing_app:
                status = [ApplicationStatus.APPROVED, ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW][i % 3]
                app = ScholarshipApplication(
                    scholarship_id=s.id,
                    student_id=student.id,
                    status=status,
                    application_date=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
                    personal_statement="I am highly motivated to pursue my studies in CS and this scholarship will help me focus on my research.",
                    financial_justification="My family annual income is limited and this grant will cover my tuition fees.",
                    ai_success_probability=0.85 if status == ApplicationStatus.APPROVED else 0.65
                )
                db.session.add(app)
        
        db.session.commit()

        # 4. Seed Counselling Requests
        print("🤝 Seeding Counselling Requests...")
        c_request = CounsellingRequest(
            student_id=student.id,
            user_id=john_user.id,
            topic="Academic Planning & Career Guidance",
            description="I need help choosing my electives for the next semester and identifying potential internships.",
            counselling_type="Academic",
            status=CounsellingStatus.SCHEDULED,
            scheduled_date=datetime.utcnow() + timedelta(days=2),
            priority="medium"
        )
        db.session.add(c_request)
        db.session.commit()

        # 5. Seed AI Interactions
        print("🤖 Seeding AI Interactions...")
        interactions = [
            {
                'user_query': "What scholarships am I eligible for?",
                'ai_response': "Based on your 3.8 GPA and CS major, you are eligible for the Global Tech Merit Scholarship and STEM Leadership Award.",
                'intent_classification': 'scholarship_query',
                'confidence_score': 0.98
            },
            {
                'user_query': "How can I improve my success rate?",
                'ai_response': "You have a high success probability. I recommend focusing on your personal statement for the STEM Leadership Award.",
                'intent_classification': 'guidance',
                'confidence_score': 0.92
            }
        ]
        
        for inter in interactions:
            ai_i = AIInteraction(
                user_id=john_user.id,
                session_id='session_seed_001',
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                **inter
            )
            db.session.add(ai_i)
        
        db.session.commit()

        # 6. Seed Analytics Data
        print("📊 Seeding Analytics Data...")
        for i in range(10):
            analytic = AnalyticsData(
                date=date.today() - timedelta(days=i),
                metric_type='engagement',
                metric_name='platform_usage_time',
                metric_value=float(random.randint(20, 120)),
                ai_trend_direction='up' if i < 5 else 'down'
            )
            db.session.add(analytic)
        
        db.session.commit()

        print("✅ Comprehensive seeding complete!")

if __name__ == "__main__":
    # First ensure basic tables and initial users exist
    # (Optional: run create_initial_data if table is empty)
    seed_comprehensive_data()
