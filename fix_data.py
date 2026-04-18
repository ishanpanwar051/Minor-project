from app import create_app
from models import User, Student, db
from models_enhanced import Scholarship, ScholarshipApplication
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # Update Rohit's GPA
    student = Student.query.filter_by(email='rohit.verma@eduguard.edu').first()
    if student:
        student.gpa = 7.0
        db.session.commit()
        print("Updated Rohit's GPA to 7.0")
    
    # Create sample scholarships
    scholarships = [
        Scholarship(
            title="Merit Scholarship",
            description="For academic excellence",
            amount=5000.0,
            min_gpa=6.5,
            status='active',
            created_by=1
        ),
        Scholarship(
            title="STEM Scholarship", 
            description="For STEM students",
            amount=7500.0,
            min_gpa=7.0,
            status='active',
            created_by=1
        )
    ]
    
    for scholarship in scholarships:
        db.session.add(scholarship)
    
    db.session.commit()
    print("Created sample scholarships")
    
    # Create sample applications
    if student:
        applications = ScholarshipApplication.query.filter_by(student_id=student.id).all()
        if len(applications) == 0:
            # Create applications
            for i, scholarship in enumerate(Scholarship.query.limit(2).all()):
                app_data = ScholarshipApplication(
                    scholarship_id=scholarship.id,
                    student_id=student.id,
                    status='pending' if i == 0 else 'approved',
                    gpa_at_application=7.0
                )
                db.session.add(app_data)
            db.session.commit()
            print("Created sample applications")
    
    print("Data setup complete!")
