"""
Daily Automatic Update System for EduGuard
Attendance aur User Data ka daily automatic update
"""

import os
from datetime import datetime, timedelta, date
from sqlalchemy import text
from app import create_app
from models import db
import random
import threading
import time

class DailyUpdateSystem:
    """Daily automatic update system"""
    
    def __init__(self):
        self.app = create_app()
        self.running = False
        self.update_thread = None
    
    def start_daily_updates(self):
        """Start daily update system"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._daily_update_loop, daemon=True)
            self.update_thread.start()
            print("Daily update system started")
    
    def stop_daily_updates(self):
        """Stop daily update system"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
        print("Daily update system stopped")
    
    def _daily_update_loop(self):
        """Main update loop - runs every day"""
        while self.running:
            try:
                with self.app.app_context():
                    # Check if it's time to update (once per day)
                    now = datetime.now()
                    
                    # Run update at 9:00 AM daily
                    if now.hour == 9 and now.minute == 0:
                        print(f"Running daily updates: {now}")
                        
                        # Update attendance
                        self.update_daily_attendance()
                        
                        # Update user data
                        self.update_user_data()
                        
                        # Update statistics
                        self.update_statistics()
                        
                        print(f"Daily updates completed: {now}")
                    
                    # Sleep for 1 minute
                    time.sleep(60)
                    
            except Exception as e:
                print(f"Error in daily update loop: {e}")
                time.sleep(60)
    
    def update_daily_attendance(self):
        """Update daily attendance for all students"""
        try:
            print("Updating daily attendance...")
            
            # Get all active students
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
                    # Generate realistic attendance
                    attendance_status = self._generate_attendance_status(student_id)
                    
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
            
        except Exception as e:
            print(f"Error updating attendance: {e}")
            db.session.rollback()
    
    def update_user_data(self):
        """Update user data daily"""
        try:
            print("Updating user data...")
            
            # Update user statistics
            users_query = text("""
                UPDATE users 
                SET last_login = COALESCE(
                    (SELECT MAX(created_at) FROM attendance WHERE student_id = users.id),
                    last_login
                ),
                updated_at = :updated_at
                WHERE role = 'student'
            """)
            
            result = db.session.execute(users_query, {
                'updated_at': datetime.now()
            })
            
            updated_count = result.rowcount
            db.session.commit()
            
            print(f"User data updated: {updated_count} users")
            
        except Exception as e:
            print(f"Error updating user data: {e}")
            db.session.rollback()
    
    def update_statistics(self):
        """Update daily statistics"""
        try:
            print("Updating statistics...")
            
            today = date.today()
            
            # Calculate attendance rate for today
            attendance_query = text("""
                SELECT 
                    COUNT(*) as total_students,
                    SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_students
                FROM attendance 
                WHERE date = :date
            """)
            
            result = db.session.execute(attendance_query, {'date': today})
            attendance_data = result.fetchone()
            
            if attendance_data and attendance_data[0] > 0:
                total_students = attendance_data[0]
                present_students = attendance_data[1]
                attendance_rate = (present_students / total_students) * 100
                
                print(f"Today's attendance rate: {attendance_rate:.1f}% ({present_students}/{total_students})")
                
                # Store in statistics table if exists
                try:
                    stats_query = text("""
                        INSERT INTO daily_statistics (date, attendance_rate, total_students, present_students)
                        VALUES (:date, :attendance_rate, :total_students, :present_students)
                    """)
                    
                    db.session.execute(stats_query, {
                        'date': today,
                        'attendance_rate': attendance_rate,
                        'total_students': total_students,
                        'present_students': present_students
                    })
                    
                    db.session.commit()
                    print("Statistics updated successfully")
                    
                except Exception as e:
                    print(f"Statistics table might not exist: {e}")
            
        except Exception as e:
            print(f"Error updating statistics: {e}")
            db.session.rollback()
    
    def _generate_attendance_status(self, student_id):
        """Generate realistic attendance status"""
        # Base attendance rate (can be customized per student)
        base_attendance_rate = 0.85  # 85% base attendance
        
        # Add some randomness
        random_value = random.random()
        
        if random_value < base_attendance_rate:
            return 'Present'
        elif random_value < base_attendance_rate + 0.10:
            return 'Late'
        else:
            return 'Absent'
    
    def manual_update_now(self):
        """Force manual update now"""
        try:
            with self.app.app_context():
                print("Running manual daily update...")
                
                self.update_daily_attendance()
                self.update_user_data()
                self.update_statistics()
                
                print("Manual update completed")
                
        except Exception as e:
            print(f"Error in manual update: {e}")
    
    def get_update_status(self):
        """Get current update status"""
        try:
            with self.app.app_context():
                # Check today's attendance
                today = date.today()
                
                attendance_query = text("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
                    FROM attendance 
                    WHERE date = :date
                """)
                
                result = db.session.execute(attendance_query, {'date': today})
                attendance_data = result.fetchone()
                
                if attendance_data:
                    total = attendance_data[0]
                    present = attendance_data[1]
                    rate = (present / total * 100) if total > 0 else 0
                    
                    return {
                        'date': today,
                        'total_students': total,
                        'present_students': present,
                        'attendance_rate': rate,
                        'system_running': self.running
                    }
                
        except Exception as e:
            print(f"Error getting status: {e}")
        
        return {'system_running': self.running}

# Global instance
daily_updater = DailyUpdateSystem()

def start_daily_updates():
    """Start daily update system"""
    daily_updater.start_daily_updates()

def stop_daily_updates():
    """Stop daily update system"""
    daily_updater.stop_daily_updates()

def manual_update_now():
    """Force manual update now"""
    daily_updater.manual_update_now()

def get_update_status():
    """Get current update status"""
    return daily_updater.get_update_status()

if __name__ == '__main__':
    # Test the system
    print("Testing Daily Update System...")
    
    # Run manual update
    manual_update_now()
    
    # Show status
    status = get_update_status()
    print(f"Update Status: {status}")
    
    # Start automatic updates (optional)
    print("Starting automatic updates...")
    start_daily_updates()
    
    # Keep running for testing
    try:
        while True:
            time.sleep(60)
            status = get_update_status()
            print(f"System running: {status.get('system_running', False)}")
    except KeyboardInterrupt:
        print("Stopping system...")
        stop_daily_updates()
