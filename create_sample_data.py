#!/usr/bin/env python3
"""
Script to create sample scholarship and application data for testing
"""

from app import create_app
from models import User, Student
from models_enhanced import Scholarship, ScholarshipApplication
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample scholarships and applications for testing"""
    app = create_app()
    
    with app.app_context():
        print("Creating sample data...")
        
        # Get Rohit's student record
        student = Student.query.filter_by(email='rohit.verma@eduguard.edu').first()
        if not student:
            print("Rohit student not found!")
            return
        
        # Update Rohit's GPA to 7.0 as requested
        student.gpa = 7.0
        
        # Create sample scholarships
        scholarships_data = [
            {
                'title': 'Merit Scholarship for Academic Excellence',
                'description': 'Awarded to students with outstanding academic performance',
                'amount': 5000.0,
                'currency': 'USD',
                'payment_frequency': 'Annual',
                'min_gpa': 6.5,
                'max_income': 50000.0,
                'required_credits': 30,
                'departments': '["Computer Science", "Engineering", "Business"]',
                'year_level': 'Sophomore',
                'nationality_requirements': 'US Citizens only',
                'gender_requirements': 'All',
                'application_deadline': datetime.utcnow() + timedelta(days=30),
                'start_date': datetime.utcnow() + timedelta(days=60),
                'end_date': datetime.utcnow() + timedelta(days=365),
                'required_documents': '["Transcript", "Essay", "Recommendation Letters"]',
                'application_process': 'Online application with essay submission',
                'status': 'active',
                'created_by': 1  # Admin user ID
            },
            {
                'title': 'Need-Based Financial Aid Scholarship',
                'description': 'For students demonstrating financial need',
                'amount': 3000.0,
                'currency': 'USD',
                'payment_frequency': 'Semester',
                'min_gpa': 3.0,
                'max_income': 30000.0,
                'required_credits': 24,
                'departments': '["All Departments"]',
                'year_level': 'All Years',
                'nationality_requirements': 'US Citizens and Permanent Residents',
                'gender_requirements': 'All',
                'application_deadline': datetime.utcnow() + timedelta(days=45),
                'start_date': datetime.utcnow() + timedelta(days=75),
                'end_date': datetime.utcnow() + timedelta(days=180),
                'required_documents': '["FAFSA", "Tax Returns", "Income Verification"]',
                'application_process': 'Financial aid application with supporting documents',
                'status': 'active',
                'created_by': 1
            },
            {
                'title': 'STEM Excellence Scholarship',
                'description': 'Encouraging students in STEM fields',
                'amount': 7500.0,
                'currency': 'USD',
                'payment_frequency': 'Annual',
                'min_gpa': 7.0,
                'max_income': 75000.0,
                'required_credits': 36,
                'departments': '["Computer Science", "Engineering", "Mathematics", "Physics"]',
                'year_level': 'Junior, Senior',
                'nationality_requirements': 'US Citizens',
                'gender_requirements': 'All',
                'application_deadline': datetime.utcnow() + timedelta(days=20),
                'start_date': datetime.utcnow() + timedelta(days=90),
                'end_date': datetime.utcnow() + timedelta(days=270),
                'required_documents': '["Transcript", "STEM Project Portfolio", "Teacher Recommendations"]',
                'application_process': 'Online application with project portfolio review',
                'status': 'active',
                'created_by': 1
            }
        ]
        
        # Create scholarships
        for scholarship_data in scholarships_data:
            scholarship = Scholarship(
                title=scholarship_data['title'],
                description=scholarship_data['description'],
                amount=scholarship_data['amount'],
                currency=scholarship_data['currency'],
                payment_frequency=scholarship_data['payment_frequency'],
                min_gpa=scholarship_data['min_gpa'],
                max_income=scholarship_data['max_income'],
                required_credits=scholarship_data['required_credits'],
                departments=str(scholarship_data['departments']),
                year_level=scholarship_data['year_level'],
                nationality_requirements=scholarship_data['nationality_requirements'],
                gender_requirements=scholarship_data['gender_requirements'],
                application_deadline=scholarship_data['application_deadline'],
                start_date=scholarship_data['start_date'],
                end_date=scholarship_data['end_date'],
                required_documents=str(scholarship_data['required_documents']),
                application_process=scholarship_data['application_process'],
                status=scholarship_data['status'],
                created_by=scholarship_data['created_by']
            )
            
            app.db.session.add(scholarship)
            print(f"Created scholarship: {scholarship.title}")
        
        # Create sample applications for Rohit
        scholarships = Scholarship.query.limit(3).all()  # Get first 3 scholarships
        for i, scholarship in enumerate(scholarships):
            application = ScholarshipApplication(
                scholarship_id=scholarship.id,
                student_id=student.id,
                application_date=datetime.utcnow() - timedelta(days=i*5),  # Different application dates
                status='pending' if i == 0 else 'approved' if i == 1 else 'rejected',
                gpa_at_application=student.gpa,
                essay_content=f"Application essay for {scholarship.title}",
                documents_submitted=str(["Transcript.pdf", f"Essay_{i+1}.pdf"]),
                ai_eligibility_score=85.0 + i*5,  # Varied scores
                ai_success_probability=0.75 + i*0.1,
                ai_recommendations=f"Strong fit for {scholarship.title}",
                reviewed_by=1  # Admin user ID
                review_date=datetime.utcnow() - timedelta(days=i*2),
                review_comments="Good academic standing" if i == 1 else "Needs improvement"
            )
            
            app.db.session.add(application)
            print(f"Created application for {scholarship.title}")
        
        # Update Rohit's GPA to 7.0 as requested
        student.gpa = 7.0
        
        # Commit all changes
        app.db.session.commit()
        print("Sample data created successfully!")
        
        print(f"\n=== SUMMARY ===")
        print(f"Created {len(scholarships)} scholarships")
        print(f"Created {len(scholarships)} applications for Rohit")
        print(f"Updated Rohit's GPA to 7.0")

if __name__ == '__main__':
    create_sample_data()
