"""
Setup Teacher Attendance System
Create teacher_attendance table and daily_attendance_reports table
"""

from sqlalchemy import text
from app import create_app
from models import db

def setup_teacher_attendance_tables():
    """Create teacher attendance tables"""
    app = create_app()
    
    with app.app_context():
        print("Setting up Teacher Attendance System...")
        
        try:
            # Create teacher_attendance table
            create_teacher_attendance_query = text("""
                CREATE TABLE IF NOT EXISTS teacher_attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    check_in_time TIME,
                    check_out_time TIME,
                    department VARCHAR(100),
                    classes_conducted INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES users (id),
                    UNIQUE(teacher_id, date)
                )
            """)
            
            db.session.execute(create_teacher_attendance_query)
            print("Teacher attendance table created/verified")
            
            # Create daily_attendance_reports table
            create_reports_query = text("""
                CREATE TABLE IF NOT EXISTS daily_attendance_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL UNIQUE,
                    student_total INTEGER DEFAULT 0,
                    student_present INTEGER DEFAULT 0,
                    student_absent INTEGER DEFAULT 0,
                    student_late INTEGER DEFAULT 0,
                    teacher_total INTEGER DEFAULT 0,
                    teacher_present INTEGER DEFAULT 0,
                    teacher_absent INTEGER DEFAULT 0,
                    teacher_late INTEGER DEFAULT 0,
                    total_classes INTEGER DEFAULT 0,
                    student_attendance_rate REAL DEFAULT 0,
                    teacher_attendance_rate REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            db.session.execute(create_reports_query)
            print("Daily attendance reports table created/verified")
            
            # Create indexes for better performance
            create_indexes_query = text("""
                CREATE INDEX IF NOT EXISTS idx_teacher_attendance_date ON teacher_attendance(date);
                CREATE INDEX IF NOT EXISTS idx_teacher_attendance_teacher ON teacher_attendance(teacher_id);
                CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_attendance_reports(date);
            """)
            
            db.session.execute(create_indexes_query)
            print("Indexes created for performance")
            
            db.session.commit()
            print("Teacher attendance system setup completed!")
            
        except Exception as e:
            print(f"Error setting up teacher attendance: {e}")
            db.session.rollback()

def create_sample_teacher_data():
    """Create sample teacher data if not exists"""
    app = create_app()
    
    with app.app_context():
        print("Creating sample teacher data...")
        
        try:
            # Check if faculty table exists and has data
            faculty_check_query = text("SELECT COUNT(*) FROM faculty")
            result = db.session.execute(faculty_check_query)
            faculty_count = result.fetchone()[0]
            
            if faculty_count == 0:
                print("Creating sample faculty records...")
                
                # Get faculty users
                faculty_users_query = text("""
                    SELECT id, first_name, last_name, email FROM users 
                    WHERE role = 'faculty' LIMIT 5
                """)
                result = db.session.execute(faculty_users_query)
                faculty_users = result.fetchall()
                
                departments = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'English']
                designations = ['Assistant Professor', 'Associate Professor', 'Professor']
                
                for i, user in enumerate(faculty_users):
                    faculty_insert_query = text("""
                        INSERT INTO faculty (user_id, employee_id, department, designation, 
                                          specialization, hire_date, status)
                        VALUES (:user_id, :employee_id, :department, :designation,
                                :specialization, :hire_date, :status)
                    """)
                    
                    db.session.execute(faculty_insert_query, {
                        'user_id': user[0],
                        'employee_id': f"EMP{user[0]:04d}",
                        'department': departments[i % len(departments)],
                        'designation': designations[i % len(designations)],
                        'specialization': f"Specialization in {departments[i % len(departments)]}",
                        'hire_date': '2023-01-15',
                        'status': 'active'
                    })
                
                db.session.commit()
                print(f"Created {len(faculty_users)} sample faculty records")
            
            else:
                print(f"Faculty records already exist: {faculty_count}")
                
        except Exception as e:
            print(f"Error creating sample teacher data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    setup_teacher_attendance_tables()
    create_sample_teacher_data()
