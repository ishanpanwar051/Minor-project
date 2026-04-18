"""
Test Daily Update System
Simple test without circular imports
"""

import os
from datetime import datetime, date
from sqlalchemy import text
from app import create_app
from models import db
import random

def test_attendance_update():
    """Test attendance update functionality"""
    app = create_app()
    
    with app.app_context():
        print("Testing Daily Attendance Update...")
        
        try:
            # Get all students
            students_query = text("SELECT id, first_name, last_name FROM students")
            result = db.session.execute(students_query)
            students = result.fetchall()
            
            today = date.today()
            updated_count = 0
            
            for student in students:
                student_id = student[0]
                student_name = f"{student[1]} {student[2]}"
                
                # Check if attendance already exists for today
                existing_query = text("""
                    SELECT COUNT(*) FROM attendance 
                    WHERE student_id = :student_id AND date = :date
                """)
                existing_result = db.session.execute(existing_query, {
                    'student_id': student_id,
                    'date': today
                })
                
                if existing_result.fetchone()[0] == 0:
                    # Generate attendance
                    attendance_status = 'Present' if random.random() < 0.85 else 'Absent'
                    
                    # Insert new attendance record
                    insert_query = text("""
                        INSERT INTO attendance (student_id, date, status, created_at)
                        VALUES (:student_id, :date, :status, :created_at)
                    """)
                    
                    db.session.execute(insert_query, {
                        'student_id': student_id,
                        'date': today,
                        'status': attendance_status,
                        'created_at': datetime.now()
                    })
                    
                    updated_count += 1
                    print(f"  Attendance updated for {student_name}: {attendance_status}")
            
            db.session.commit()
            print(f"Daily attendance updated: {updated_count} students")
            
            # Show statistics
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_students,
                    SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_students
                FROM attendance 
                WHERE date = :date
            """)
            
            result = db.session.execute(stats_query, {'date': today})
            stats = result.fetchone()
            
            if stats and stats[0] > 0:
                attendance_rate = (stats[1] / stats[0]) * 100
                print(f"Today's attendance rate: {attendance_rate:.1f}% ({stats[1]}/{stats[0]})")
            
        except Exception as e:
            print(f"Error updating attendance: {e}")
            db.session.rollback()

def test_user_data_update():
    """Test user data update functionality"""
    app = create_app()
    
    with app.app_context():
        print("Testing User Data Update...")
        
        try:
            # Update user statistics
            users_query = text("""
                UPDATE users 
                SET updated_at = :updated_at
                WHERE role = 'student'
            """)
            
            result = db.session.execute(users_query, {
                'updated_at': datetime.now()
            })
            
            updated_count = result.rowcount
            db.session.commit()
            
            print(f"User data updated: {updated_count} users")
            
            # Show user statistics
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_users,
                    SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) as students,
                    SUM(CASE WHEN role = 'faculty' THEN 1 ELSE 0 END) as faculty,
                    SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admins
                FROM users
            """)
            
            result = db.session.execute(stats_query)
            stats = result.fetchone()
            
            print(f"User Statistics:")
            print(f"  Total Users: {stats[0]}")
            print(f"  Students: {stats[1]}")
            print(f"  Faculty: {stats[2]}")
            print(f"  Admins: {stats[3]}")
            
        except Exception as e:
            print(f"Error updating user data: {e}")
            db.session.rollback()

def create_daily_statistics_table():
    """Create daily statistics table if not exists"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create table for daily statistics
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS daily_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    attendance_rate REAL,
                    total_students INTEGER,
                    present_students INTEGER,
                    absent_students INTEGER,
                    late_students INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            db.session.execute(create_table_query)
            db.session.commit()
            print("Daily statistics table created/verified")
            
        except Exception as e:
            print(f"Error creating statistics table: {e}")

def main():
    """Main test function"""
    print("=== DAILY UPDATE SYSTEM TEST ===")
    print()
    
    # Create statistics table
    create_daily_statistics_table()
    
    # Test attendance update
    test_attendance_update()
    print()
    
    # Test user data update
    test_user_data_update()
    print()
    
    print("=== TEST COMPLETED ===")
    print()
    print("Next Steps:")
    print("1. Start the Flask application")
    print("2. Login as admin (admin@eduguard.edu / admin123)")
    print("3. Go to /update/dashboard to control the system")
    print("4. Use the dashboard to start/stop daily updates")

if __name__ == '__main__':
    main()
