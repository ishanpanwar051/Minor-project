"""
Complete Daily Attendance System for EduGuard
Students aur Teachers dono ke liye automatic daily attendance
"""

import os
from datetime import datetime, date, timedelta
from sqlalchemy import text
from app import create_app
from models import db
import random
import threading
import time

class CompleteAttendanceSystem:
    """Complete attendance system for students and teachers"""
    
    def __init__(self):
        self.app = create_app()
        self.running = False
        self.update_thread = None
    
    def start_system(self):
        """Start automatic attendance system"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._attendance_loop, daemon=True)
            self.update_thread.start()
            print("Complete Attendance System started")
    
    def stop_system(self):
        """Stop automatic attendance system"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
        print("Complete Attendance System stopped")
    
    def _attendance_loop(self):
        """Main attendance loop - runs every day"""
        while self.running:
            try:
                with self.app.app_context():
                    now = datetime.now()
                    
                    # Run update at 8:00 AM daily (before school starts)
                    if now.hour == 8 and now.minute == 0:
                        print(f"Running daily attendance: {now}")
                        
                        # Update student attendance
                        self.update_student_attendance()
                        
                        # Update teacher attendance
                        self.update_teacher_attendance()
                        
                        # Generate attendance reports
                        self.generate_attendance_reports()
                        
                        print(f"Daily attendance completed: {now}")
                    
                    # Sleep for 1 minute
                    time.sleep(60)
                    
            except Exception as e:
                print(f"Error in attendance loop: {e}")
                time.sleep(60)
    
    def update_student_attendance(self):
        """Update daily attendance for all students"""
        try:
            print("Updating student attendance...")
            
            # Get all active students
            students_query = text("""
                SELECT id, first_name, last_name, email, gpa 
                FROM students 
                WHERE status = 'active' OR status IS NULL
            """)
            result = db.session.execute(students_query)
            students = result.fetchall()
            
            today = date.today()
            updated_count = 0
            present_count = 0
            absent_count = 0
            late_count = 0
            
            for student in students:
                student_id = student[0]
                student_name = f"{student[1]} {student[2]}"
                student_email = student[3]
                student_gpa = student[4]
                
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
                    # Generate realistic attendance based on GPA and patterns
                    attendance_status = self._generate_student_attendance(student_gpa, student_id)
                    
                    # Insert new attendance record
                    insert_query = text("""
                        INSERT INTO attendance (student_id, date, status, check_in_time, check_out_time)
                        VALUES (:student_id, :date, :status, :check_in_time, :check_out_time)
                    """)
                    
                    check_in_time = self._generate_check_in_time(attendance_status)
                    check_out_time = self._generate_check_out_time(attendance_status, check_in_time)
                    
                    db.session.execute(insert_query, {
                        'student_id': student_id,
                        'date': today,
                        'status': attendance_status,
                        'check_in_time': check_in_time,
                        'check_out_time': check_out_time
                    })
                    
                    updated_count += 1
                    
                    if attendance_status == 'Present':
                        present_count += 1
                    elif attendance_status == 'Absent':
                        absent_count += 1
                    elif attendance_status == 'Late':
                        late_count += 1
                    
                    print(f"  Student: {student_name} - {attendance_status} ({check_in_time})")
            
            db.session.commit()
            
            attendance_rate = (present_count / updated_count * 100) if updated_count > 0 else 0
            print(f"Student Attendance Summary:")
            print(f"  Total Updated: {updated_count}")
            print(f"  Present: {present_count}")
            print(f"  Absent: {absent_count}")
            print(f"  Late: {late_count}")
            print(f"  Attendance Rate: {attendance_rate:.1f}%")
            
        except Exception as e:
            print(f"Error updating student attendance: {e}")
            db.session.rollback()
    
    def update_teacher_attendance(self):
        """Update daily attendance for all teachers"""
        try:
            print("Updating teacher attendance...")
            
            # Get all active teachers (faculty users)
            teachers_query = text("""
                SELECT u.id, u.first_name, u.last_name, u.email, f.department, f.designation
                FROM users u
                JOIN faculty f ON u.id = f.user_id
                WHERE u.role = 'faculty' AND u.status = 'active'
            """)
            result = db.session.execute(teachers_query)
            teachers = result.fetchall()
            
            today = date.today()
            updated_count = 0
            present_count = 0
            absent_count = 0
            late_count = 0
            
            for teacher in teachers:
                teacher_id = teacher[0]
                teacher_name = f"{teacher[1]} {teacher[2]}"
                teacher_email = teacher[3]
                department = teacher[4]
                designation = teacher[5]
                
                # Check if teacher attendance already exists for today
                existing_query = text("""
                    SELECT COUNT(*) FROM teacher_attendance 
                    WHERE teacher_id = :teacher_id AND date = :date
                """)
                existing_result = db.session.execute(existing_query, {
                    'teacher_id': teacher_id,
                    'date': today
                })
                
                if existing_result.fetchone()[0] == 0:
                    # Generate realistic teacher attendance
                    attendance_status = self._generate_teacher_attendance(department, designation)
                    
                    # Insert teacher attendance record
                    insert_query = text("""
                        INSERT INTO teacher_attendance 
                        (teacher_id, date, status, check_in_time, check_out_time, department, classes_conducted)
                        VALUES (:teacher_id, :date, :status, :check_in_time, :check_out_time, :department, :classes_conducted)
                    """)
                    
                    check_in_time = self._generate_teacher_check_in_time(attendance_status)
                    check_out_time = self._generate_teacher_check_out_time(attendance_status, check_in_time)
                    classes_conducted = self._generate_classes_conducted(attendance_status, designation)
                    
                    db.session.execute(insert_query, {
                        'teacher_id': teacher_id,
                        'date': today,
                        'status': attendance_status,
                        'check_in_time': check_in_time,
                        'check_out_time': check_out_time,
                        'department': department,
                        'classes_conducted': classes_conducted
                    })
                    
                    updated_count += 1
                    
                    if attendance_status == 'Present':
                        present_count += 1
                    elif attendance_status == 'Absent':
                        absent_count += 1
                    elif attendance_status == 'Late':
                        late_count += 1
                    
                    print(f"  Teacher: {teacher_name} ({department}) - {attendance_status} ({classes_conducted} classes)")
            
            db.session.commit()
            
            attendance_rate = (present_count / updated_count * 100) if updated_count > 0 else 0
            print(f"Teacher Attendance Summary:")
            print(f"  Total Updated: {updated_count}")
            print(f"  Present: {present_count}")
            print(f"  Absent: {absent_count}")
            print(f"  Late: {late_count}")
            print(f"  Attendance Rate: {attendance_rate:.1f}%")
            
        except Exception as e:
            print(f"Error updating teacher attendance: {e}")
            db.session.rollback()
    
    def generate_attendance_reports(self):
        """Generate daily attendance reports"""
        try:
            print("Generating attendance reports...")
            
            today = date.today()
            
            # Student attendance report
            student_report_query = text("""
                SELECT 
                    COUNT(*) as total_students,
                    SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_students,
                    SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent_students,
                    SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late_students
                FROM attendance 
                WHERE date = :date
            """)
            
            student_result = db.session.execute(student_report_query, {'date': today})
            student_stats = student_result.fetchone()
            
            # Teacher attendance report
            teacher_report_query = text("""
                SELECT 
                    COUNT(*) as total_teachers,
                    SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_teachers,
                    SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent_teachers,
                    SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late_teachers,
                    SUM(classes_conducted) as total_classes
                FROM teacher_attendance 
                WHERE date = :date
            """)
            
            teacher_result = db.session.execute(teacher_report_query, {'date': today})
            teacher_stats = teacher_result.fetchone()
            
            # Store in daily reports table
            try:
                insert_report_query = text("""
                    INSERT INTO daily_attendance_reports 
                    (date, student_total, student_present, student_absent, student_late,
                     teacher_total, teacher_present, teacher_absent, teacher_late, total_classes, created_at)
                    VALUES (:date, :student_total, :student_present, :student_absent, :student_late,
                            :teacher_total, :teacher_present, :teacher_absent, :teacher_late, :total_classes, :created_at)
                """)
                
                db.session.execute(insert_report_query, {
                    'date': today,
                    'student_total': student_stats[0] if student_stats else 0,
                    'student_present': student_stats[1] if student_stats else 0,
                    'student_absent': student_stats[2] if student_stats else 0,
                    'student_late': student_stats[3] if student_stats else 0,
                    'teacher_total': teacher_stats[0] if teacher_stats else 0,
                    'teacher_present': teacher_stats[1] if teacher_stats else 0,
                    'teacher_absent': teacher_stats[2] if teacher_stats else 0,
                    'teacher_late': teacher_stats[3] if teacher_stats else 0,
                    'total_classes': teacher_stats[4] if teacher_stats else 0,
                    'created_at': datetime.now()
                })
                
                db.session.commit()
                print("Daily attendance report generated")
                
            except Exception as e:
                print(f"Error storing report: {e}")
            
            # Print summary
            print(f"Daily Attendance Report for {today}:")
            print(f"  Students: {student_stats[1] if student_stats else 0}/{student_stats[0] if student_stats else 0} present")
            print(f"  Teachers: {teacher_stats[1] if teacher_stats else 0}/{teacher_stats[0] if teacher_stats else 0} present")
            print(f"  Total Classes: {teacher_stats[4] if teacher_stats else 0}")
            
        except Exception as e:
            print(f"Error generating reports: {e}")
    
    def _generate_student_attendance(self, gpa, student_id):
        """Generate realistic student attendance based on GPA"""
        # Higher GPA = higher attendance rate
        if gpa >= 8.0:
            base_rate = 0.95  # 95% attendance
        elif gpa >= 7.0:
            base_rate = 0.90  # 90% attendance
        elif gpa >= 6.0:
            base_rate = 0.80  # 80% attendance
        else:
            base_rate = 0.70  # 70% attendance
        
        # Add some randomness
        random_value = random.random()
        
        if random_value < base_rate:
            return 'Present'
        elif random_value < base_rate + 0.10:
            return 'Late'
        else:
            return 'Absent'
    
    def _generate_teacher_attendance(self, department, designation):
        """Generate realistic teacher attendance"""
        # Teachers generally have higher attendance
        base_rate = 0.95  # 95% base attendance
        
        # Department-specific adjustments
        if department == 'Computer Science':
            base_rate = 0.98
        elif department == 'Mathematics':
            base_rate = 0.96
        elif department == 'Physics':
            base_rate = 0.94
        
        # Designation-specific adjustments
        if 'Professor' in designation:
            base_rate = 0.97
        elif 'Assistant' in designation:
            base_rate = 0.95
        
        random_value = random.random()
        
        if random_value < base_rate:
            return 'Present'
        elif random_value < base_rate + 0.03:
            return 'Late'
        else:
            return 'Absent'
    
    def _generate_check_in_time(self, status):
        """Generate check-in time based on status"""
        if status == 'Present':
            # On time: 8:00 AM - 8:30 AM
            hour = 8 + random.randint(0, 0)
            minute = random.randint(0, 30)
        elif status == 'Late':
            # Late: 8:31 AM - 9:30 AM
            hour = 8 + random.randint(0, 1)
            minute = random.randint(31, 59) if hour == 8 else random.randint(0, 30)
        else:
            return None
        
        return f"{hour:02d}:{minute:02d}"
    
    def _generate_check_out_time(self, status, check_in_time):
        """Generate check-out time based on status and check-in time"""
        if status == 'Absent' or not check_in_time:
            return None
        
        # Check-out: 2:00 PM - 4:00 PM
        hour = random.randint(14, 16)
        minute = random.randint(0, 59)
        
        return f"{hour:02d}:{minute:02d}"
    
    def _generate_teacher_check_in_time(self, status):
        """Generate teacher check-in time"""
        if status == 'Present':
            # Teachers arrive earlier: 7:30 AM - 8:00 AM
            hour = 7 + random.randint(0, 1)
            minute = random.randint(30, 59) if hour == 7 else random.randint(0, 0)
        elif status == 'Late':
            # Late: 8:01 AM - 9:00 AM
            hour = 8 + random.randint(0, 1)
            minute = random.randint(1, 59) if hour == 8 else random.randint(0, 0)
        else:
            return None
        
        return f"{hour:02d}:{minute:02d}"
    
    def _generate_teacher_check_out_time(self, status, check_in_time):
        """Generate teacher check-out time"""
        if status == 'Absent' or not check_in_time:
            return None
        
        # Teachers stay later: 3:00 PM - 5:00 PM
        hour = random.randint(15, 17)
        minute = random.randint(0, 59)
        
        return f"{hour:02d}:{minute:02d}"
    
    def _generate_classes_conducted(self, status, designation):
        """Generate number of classes conducted"""
        if status == 'Absent':
            return 0
        
        if 'Professor' in designation:
            return random.randint(2, 4)
        elif 'Assistant' in designation:
            return random.randint(3, 5)
        else:
            return random.randint(2, 4)
    
    def manual_update_now(self):
        """Force manual update now"""
        try:
            with self.app.app_context():
                print("Running manual complete attendance update...")
                
                self.update_student_attendance()
                self.update_teacher_attendance()
                self.generate_attendance_reports()
                
                print("Manual complete attendance update completed")
                
        except Exception as e:
            print(f"Error in manual update: {e}")
    
    def get_attendance_status(self):
        """Get current attendance status"""
        try:
            with self.app.app_context():
                today = date.today()
                
                # Student attendance
                student_query = text("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
                           SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent,
                           SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late
                    FROM attendance 
                    WHERE date = :date
                """)
                
                student_result = db.session.execute(student_query, {'date': today})
                student_stats = student_result.fetchone()
                
                # Teacher attendance
                teacher_query = text("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
                           SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent,
                           SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late,
                           SUM(classes_conducted) as total_classes
                    FROM teacher_attendance 
                    WHERE date = :date
                """)
                
                teacher_result = db.session.execute(teacher_query, {'date': today})
                teacher_stats = teacher_result.fetchone()
                
                return {
                    'date': today,
                    'student_attendance': {
                        'total': student_stats[0] if student_stats else 0,
                        'present': student_stats[1] if student_stats else 0,
                        'absent': student_stats[2] if student_stats else 0,
                        'late': student_stats[3] if student_stats else 0,
                        'rate': (student_stats[1] / student_stats[0] * 100) if student_stats and student_stats[0] > 0 else 0
                    },
                    'teacher_attendance': {
                        'total': teacher_stats[0] if teacher_stats else 0,
                        'present': teacher_stats[1] if teacher_stats else 0,
                        'absent': teacher_stats[2] if teacher_stats else 0,
                        'late': teacher_stats[3] if teacher_stats else 0,
                        'total_classes': teacher_stats[4] if teacher_stats else 0,
                        'rate': (teacher_stats[1] / teacher_stats[0] * 100) if teacher_stats and teacher_stats[0] > 0 else 0
                    },
                    'system_running': self.running
                }
                
        except Exception as e:
            print(f"Error getting status: {e}")
            return {'system_running': self.running}

# Global instance
attendance_system = CompleteAttendanceSystem()

def start_attendance_system():
    """Start attendance system"""
    attendance_system.start_system()

def stop_attendance_system():
    """Stop attendance system"""
    attendance_system.stop_system()

def manual_attendance_update():
    """Force manual attendance update"""
    attendance_system.manual_update_now()

def get_attendance_status():
    """Get current attendance status"""
    return attendance_system.get_attendance_status()

if __name__ == '__main__':
    # Test the complete attendance system
    print("Testing Complete Attendance System...")
    
    # Run manual update
    manual_attendance_update()
    
    # Show status
    status = get_attendance_status()
    print(f"Attendance Status: {status}")
    
    # Start automatic updates (optional)
    print("Starting automatic attendance updates...")
    start_attendance_system()
    
    # Keep running for testing
    try:
        while True:
            time.sleep(60)
            status = get_attendance_status()
            print(f"System running: {status.get('system_running', False)}")
    except KeyboardInterrupt:
        print("Stopping system...")
        stop_attendance_system()
