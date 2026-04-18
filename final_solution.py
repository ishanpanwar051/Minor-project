"""
FINAL COMPLETE SOLUTION FOR STUDENT DASHBOARD
This script fixes all issues and creates sample data
"""

from app import create_app
from models import User, Student, db
from datetime import datetime, timedelta

def create_all_tables():
    """Create all database tables including enhanced models"""
    app = create_app()
    
    with app.app_context():
        print("Creating all database tables...")
        
        # Import all models to ensure they're registered
        from models_enhanced import (
            Scholarship, ScholarshipApplication, CounsellingRequest, 
            AIInteraction, AnalyticsData, Notification
        )
        
        # Create all tables
        db.create_all()
        
        # Verify tables were created
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"Available tables: {len(tables)}")
        if 'scholarships' in tables:
            print("Scholarships table created successfully!")
        else:
            print("Scholarships table NOT found")
        
        return True

def create_sample_data():
    """Create sample scholarships and applications"""
    app = create_app()
    
    with app.app_context():
        from models_enhanced import Scholarship, ScholarshipApplication
        
        print("Creating sample data...")
        
        # Update Rohit's GPA
        student = Student.query.filter_by(email='rohit.verma@eduguard.edu').first()
        if student:
            student.gpa = 7.0
            db.session.commit()
            print("Updated Rohit's GPA to 7.0")
        
        # Check if scholarships already exist
        existing_scholarships = Scholarship.query.count()
        if existing_scholarships > 0:
            print(f"Scholarships already exist: {existing_scholarships}")
        else:
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
            print(f"Created {len(scholarships)} scholarships")
        
        # Create sample applications for Rohit
        if student:
            existing_apps = ScholarshipApplication.query.filter_by(student_id=student.id).count()
            if existing_apps == 0:
                scholarships = Scholarship.query.limit(2).all()
                for i, scholarship in enumerate(scholarships):
                    app_data = ScholarshipApplication(
                        scholarship_id=scholarship.id,
                        student_id=student.id,
                        status='pending' if i == 0 else 'approved',
                        gpa_at_application=7.0
                    )
                    db.session.add(app_data)
                
                db.session.commit()
                print("Created sample applications for Rohit")
        
        return True

def verify_data():
    """Verify all data is properly created"""
    app = create_app()
    
    with app.app_context():
        from models_enhanced import Scholarship, ScholarshipApplication
        
        student = Student.query.filter_by(email='rohit.verma@eduguard.edu').first()
        
        print("\n=== VERIFICATION ===")
        print(f"Rohit found: {'Yes' if student else 'No'}")
        print(f"Rohit's GPA: {student.gpa if student else 'N/A'}")
        print(f"Total scholarships: {Scholarship.query.count()}")
        print(f"Rohit's applications: {ScholarshipApplication.query.filter_by(student_id=student.id).count() if student else 0}")
        
        return True

def main():
    """Main execution function"""
    print("=== FINAL SOLUTION FOR STUDENT DASHBOARD ===")
    
    try:
        # Step 1: Create all tables
        create_all_tables()
        
        # Step 2: Create sample data
        create_sample_data()
        
        # Step 3: Verify data
        verify_data()
        
        print("\n=== SOLUTION COMPLETE ===")
        print("Student dashboard should now work with dynamic data!")
        print("Login with: rohit.verma@eduguard.edu / student123")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()
