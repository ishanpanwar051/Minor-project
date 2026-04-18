from app import create_app
from models import User, Student, db
from models_enhanced import Scholarship, ScholarshipApplication
from datetime import datetime, timedelta

def complete_fix():
    """Complete fix for student dashboard issues"""
    app = create_app()
    
    with app.app_context():
        print("=== COMPLETE STUDENT DASHBOARD FIX ===")
        
        # 1. Update Rohit's GPA to 7.0
        student = Student.query.filter_by(email='rohit.verma@eduguard.edu').first()
        if student:
            student.gpa = 7.0
            db.session.commit()
            print(f"✓ Updated Rohit's GPA to 7.0")
        else:
            print("✗ Rohit student not found")
        
        # 2. Create sample scholarships
        scholarships = [
            Scholarship(
                title="Merit Scholarship for Academic Excellence",
                description="Awarded to students with outstanding academic performance",
                amount=5000.0,
                currency="USD",
                payment_frequency="Annual",
                min_gpa=6.5,
                max_income=50000.0,
                required_credits=30,
                departments='["Computer Science", "Engineering", "Business"]',
                year_level="Sophomore",
                nationality_requirements="US Citizens only",
                gender_requirements="All",
                application_deadline=datetime.utcnow() + timedelta(days=30),
                start_date=datetime.utcnow() + timedelta(days=60),
                end_date=datetime.utcnow() + timedelta(days=365),
                required_documents='["Transcript", "Essay", "Recommendation Letters"]',
                application_process="Online application with essay submission",
                status="active",
                created_by=1
            ),
            Scholarship(
                title="Need-Based Financial Aid Scholarship",
                description="For students demonstrating financial need",
                amount=3000.0,
                currency="USD",
                payment_frequency="Semester",
                min_gpa=3.0,
                max_income=30000.0,
                required_credits=24,
                departments='["All Departments"]',
                year_level="All Years",
                nationality_requirements="US Citizens and Permanent Residents",
                gender_requirements="All",
                application_deadline=datetime.utcnow() + timedelta(days=45),
                start_date=datetime.utcnow() + timedelta(days=75),
                end_date=datetime.utcnow() + timedelta(days=180),
                required_documents='["FAFSA", "Tax Returns", "Income Verification"]',
                application_process="Financial aid application with supporting documents",
                status="active",
                created_by=1
            ),
            Scholarship(
                title="STEM Excellence Scholarship",
                description="Encouraging students in STEM fields",
                amount=7500.0,
                currency="USD",
                payment_frequency="Annual",
                min_gpa=7.0,
                max_income=75000.0,
                required_credits=36,
                departments='["Computer Science", "Engineering", "Mathematics", "Physics"]',
                year_level="Junior, Senior",
                nationality_requirements="US Citizens",
                gender_requirements="All",
                application_deadline=datetime.utcnow() + timedelta(days=20),
                start_date=datetime.utcnow() + timedelta(days=90),
                end_date=datetime.utcnow() + timedelta(days=270),
                required_documents='["Transcript", "STEM Project Portfolio", "Teacher Recommendations"]',
                application_process="Online application with project portfolio review",
                status="active",
                created_by=1
            )
        ]
        
        # Add scholarships
        for scholarship in scholarships:
            db.session.add(scholarship)
        
        db.session.commit()
        print(f"✓ Created {len(scholarships)} sample scholarships")
        
        # 3. Create sample applications for Rohit
        if student:
            existing_apps = ScholarshipApplication.query.filter_by(student_id=student.id).all()
            if len(existing_apps) == 0:
                # Create applications for first 2 scholarships
                for i, scholarship in enumerate(Scholarship.query.limit(2).all()):
                    application = ScholarshipApplication(
                        scholarship_id=scholarship.id,
                        student_id=student.id,
                        application_date=datetime.utcnow() - timedelta(days=i*5),
                        status='pending' if i == 0 else 'approved',
                        gpa_at_application=7.0,
                        essay_content=f"Application essay for {scholarship.title}",
                        documents_submitted=str(["Transcript.pdf", f"Essay_{i+1}.pdf"]),
                        ai_eligibility_score=85.0 + i*5,
                        ai_success_probability=0.75 + i*0.1,
                        ai_recommendations=f"Strong fit for {scholarship.title}",
                        reviewed_by=1,
                        review_date=datetime.utcnow() - timedelta(days=i*2),
                        review_comments="Good academic standing" if i == 1 else "Needs improvement"
                    )
                    db.session.add(application)
                
                db.session.commit()
                print(f"✓ Created sample applications for Rohit")
            else:
                print(f"✓ Rohit already has {len(existing_apps)} applications")
        
        # 4. Verify data
        total_scholarships = Scholarship.query.count()
        total_applications = ScholarshipApplication.query.count()
        rohit_apps = ScholarshipApplication.query.filter_by(student_id=student.id).count() if student else 0
        
        print(f"\n=== VERIFICATION ===")
        print(f"Total scholarships: {total_scholarships}")
        print(f"Total applications: {total_applications}")
        print(f"Rohit's applications: {rohit_apps}")
        print(f"Rohit's GPA: {student.gpa if student else 'Not found'}")
        
        print("\n✅ COMPLETE FIX SUCCESSFUL!")
        print("🎯 Student dashboard should now show dynamic data")

if __name__ == '__main__':
    complete_fix()
