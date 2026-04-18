"""
DIRECT FIX FOR STUDENT DASHBOARD
Manually creates tables and data without relying on complex imports
"""

from app import create_app
from models import User, Student, db
from datetime import datetime, timedelta
from sqlalchemy import text

def create_scholarships_table():
    """Manually create scholarships table"""
    app = create_app()
    
    with app.app_context():
        # Create table directly with SQL
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS scholarships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                amount FLOAT DEFAULT 0.0,
                min_gpa FLOAT DEFAULT 0.0,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER
            )
        '''))
        
        # Create scholarship_applications table
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS scholarship_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scholarship_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                gpa_at_application FLOAT DEFAULT 0.0,
                application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scholarship_id) REFERENCES scholarships (id),
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        '''))
        db.session.commit()
        
        print("Created scholarships and scholarship_applications tables")

def create_sample_data():
    """Insert sample data directly"""
    app = create_app()
    
    with app.app_context():
        # Update Rohit's GPA
        db.session.execute(text("UPDATE students SET gpa = 7.0 WHERE email = 'rohit.verma@eduguard.edu'"))
        print("Updated Rohit's GPA to 7.0")
        
        # Insert sample scholarships
        db.session.execute(text('''
            INSERT OR IGNORE INTO scholarships (title, description, amount, min_gpa, status, created_by)
            VALUES 
                ('Merit Scholarship', 'For academic excellence', 5000.0, 6.5, 'active', 1),
                ('STEM Scholarship', 'For STEM students', 7500.0, 7.0, 'active', 1)
        '''))
        print("Inserted sample scholarships")
        
        # Get Rohit's student ID
        result = db.session.execute(text("SELECT id FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
        student_row = result.fetchone()
        
        if student_row:
            student_id = student_row[0]
            
            # Insert sample applications for Rohit
            db.session.execute(text(f'''
                INSERT OR IGNORE INTO scholarship_applications (scholarship_id, student_id, status, gpa_at_application)
                VALUES 
                    (1, {student_id}, 'pending', 7.0),
                    (2, {student_id}, 'approved', 7.0)
            '''))
            print("Created sample applications for Rohit")
        
        db.session.commit()

def verify_data():
    """Verify the data was created"""
    app = create_app()
    
    with app.app_context():
        # Check Rohit's data
        result = db.session.execute(text("SELECT gpa FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
        student_row = result.fetchone()
        
        # Check scholarships
        result = db.session.execute(text("SELECT COUNT(*) FROM scholarships"))
        scholarship_count = result.fetchone()[0]
        
        # Check applications
        result = db.session.execute(text("SELECT COUNT(*) FROM scholarship_applications"))
        application_count = result.fetchone()[0]
        
        print("\n=== VERIFICATION ===")
        print(f"Rohit's GPA: {student_row[0] if student_row else 'Not found'}")
        print(f"Total scholarships: {scholarship_count}")
        print(f"Total applications: {application_count}")
        
        if student_row and student_row[0] == 7.0 and scholarship_count > 0 and application_count > 0:
            print("SUCCESS: All data created correctly!")
            return True
        else:
            print("ERROR: Data creation incomplete")
            return False

def main():
    """Main execution"""
    print("=== DIRECT FIX FOR STUDENT DASHBOARD ===")
    
    try:
        create_scholarships_table()
        create_sample_data()
        success = verify_data()
        
        if success:
            print("\n=== FIX COMPLETE ===")
            print("Student dashboard should now show dynamic data!")
            print("Login with: rohit.verma@eduguard.edu / student123")
        else:
            print("\n=== FIX FAILED ===")
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()
