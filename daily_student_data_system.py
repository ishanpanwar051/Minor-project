"""
Complete Daily Student Data Update System
Students ke liye daily basis par automatic data updates
"""

import os
from datetime import datetime, date, timedelta
from sqlalchemy import text
from app import create_app
from models import db
import random
import threading
import time

class DailyStudentDataSystem:
    """Daily student data update system"""
    
    def __init__(self):
        self.app = create_app()
        self.running = False
        self.update_thread = None
    
    def start_system(self):
        """Start daily student data update system"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._daily_update_loop, daemon=True)
            self.update_thread.start()
            print("Daily Student Data System started")
    
    def stop_system(self):
        """Stop daily student data update system"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
        print("Daily Student Data System stopped")
    
    def _daily_update_loop(self):
        """Main update loop - runs every day"""
        while self.running:
            try:
                with self.app.app_context():
                    now = datetime.now()
                    
                    # Run update at 9:00 PM daily (end of day)
                    if now.hour == 21 and now.minute == 0:
                        print(f"Running daily student data updates: {now}")
                        
                        # Update student performance
                        self.update_student_performance()
                        
                        # Update student activities
                        self.update_student_activities()
                        
                        # Update student progress
                        self.update_student_progress()
                        
                        # Update student statistics
                        self.update_student_statistics()
                        
                        # Generate daily reports
                        self.generate_student_reports()
                        
                        print(f"Daily student data updates completed: {now}")
                    
                    # Sleep for 1 minute
                    time.sleep(60)
                    
            except Exception as e:
                print(f"Error in daily update loop: {e}")
                time.sleep(60)
    
    def update_student_performance(self):
        """Update student performance data"""
        try:
            print("Updating student performance...")
            
            # Get all students
            students_query = text("""
                SELECT id, first_name, last_name, email, gpa, semester, year
                FROM students
            """)
            result = db.session.execute(students_query)
            students = result.fetchall()
            
            today = date.today()
            updated_count = 0
            
            for student in students:
                student_id = student[0]
                student_name = f"{student[1]} {student[2]}"
                current_gpa = student[4] or 0.0
                semester = student[5] or 1
                year = student[6] or 1
                
                # Generate performance metrics
                study_hours = self._generate_study_hours(current_gpa)
                assignment_completion = self._generate_assignment_completion(current_gpa)
                class_participation = self._generate_class_participation(current_gpa)
                test_performance = self._generate_test_performance(current_gpa)
                
                # Check if performance record exists for today
                existing_query = text("""
                    SELECT COUNT(*) FROM student_performance 
                    WHERE student_id = :student_id AND date = :date
                """)
                existing_result = db.session.execute(existing_query, {
                    'student_id': student_id,
                    'date': today
                })
                
                if existing_result.fetchone()[0] == 0:
                    # Insert new performance record
                    insert_query = text("""
                        INSERT INTO student_performance 
                        (student_id, date, study_hours, assignment_completion, 
                         class_participation, test_performance, gpa_trend, created_at)
                        VALUES (:student_id, :date, :study_hours, :assignment_completion,
                                :class_participation, :test_performance, :gpa_trend, :created_at)
                    """)
                    
                    gpa_trend = self._calculate_gpa_trend(current_gpa, test_performance)
                    
                    db.session.execute(insert_query, {
                        'student_id': student_id,
                        'date': today,
                        'study_hours': study_hours,
                        'assignment_completion': assignment_completion,
                        'class_participation': class_participation,
                        'test_performance': test_performance,
                        'gpa_trend': gpa_trend,
                        'created_at': datetime.now()
                    })
                    
                    updated_count += 1
                    print(f"  Performance updated for {student_name}: GPA {current_gpa} -> {test_performance}")
            
            db.session.commit()
            print(f"Student performance updated: {updated_count} students")
            
        except Exception as e:
            print(f"Error updating student performance: {e}")
            db.session.rollback()
    
    def update_student_activities(self):
        """Update student activities data"""
        try:
            print("Updating student activities...")
            
            # Get all students
            students_query = text("SELECT id, first_name, last_name FROM students")
            result = db.session.execute(students_query)
            students = result.fetchall()
            
            today = date.today()
            updated_count = 0
            
            for student in students:
                student_id = student[0]
                student_name = f"{student[1]} {student[2]}"
                
                # Generate activity data
                library_visits = random.randint(0, 2)
                lab_sessions = random.randint(0, 3)
                sports_participation = random.randint(0, 1)
                extracurricular = random.randint(0, 2)
                online_courses = random.randint(0, 1)
                
                # Check if activity record exists for today
                existing_query = text("""
                    SELECT COUNT(*) FROM student_activities 
                    WHERE student_id = :student_id AND date = :date
                """)
                existing_result = db.session.execute(existing_query, {
                    'student_id': student_id,
                    'date': today
                })
                
                if existing_result.fetchone()[0] == 0:
                    # Insert new activity record
                    insert_query = text("""
                        INSERT INTO student_activities 
                        (student_id, date, library_visits, lab_sessions, 
                         sports_participation, extracurricular, online_courses, created_at)
                        VALUES (:student_id, :date, :library_visits, :lab_sessions,
                                :sports_participation, :extracurricular, :online_courses, :created_at)
                    """)
                    
                    db.session.execute(insert_query, {
                        'student_id': student_id,
                        'date': today,
                        'library_visits': library_visits,
                        'lab_sessions': lab_sessions,
                        'sports_participation': sports_participation,
                        'extracurricular': extracurricular,
                        'online_courses': online_courses,
                        'created_at': datetime.now()
                    })
                    
                    updated_count += 1
                    print(f"  Activities updated for {student_name}: Library {library_visits}, Lab {lab_sessions}")
            
            db.session.commit()
            print(f"Student activities updated: {updated_count} students")
            
        except Exception as e:
            print(f"Error updating student activities: {e}")
            db.session.rollback()
    
    def update_student_progress(self):
        """Update student progress data"""
        try:
            print("Updating student progress...")
            
            # Get all students
            students_query = text("""
                SELECT id, first_name, last_name, gpa, semester, year
                FROM students
            """)
            result = db.session.execute(students_query)
            students = result.fetchall()
            
            today = date.today()
            updated_count = 0
            
            for student in students:
                student_id = student[0]
                student_name = f"{student[1]} {student[2]}"
                current_gpa = student[3] or 0.0
                semester = student[4] or 1
                year = student[5] or 1
                
                # Generate progress metrics
                credits_completed = self._calculate_credits_completed(year, semester)
                courses_in_progress = self._calculate_courses_in_progress(semester)
                academic_standing = self._calculate_academic_standing(current_gpa)
                graduation_progress = self._calculate_graduation_progress(year, semester)
                
                # Check if progress record exists for today
                existing_query = text("""
                    SELECT COUNT(*) FROM student_progress 
                    WHERE student_id = :student_id AND date = :date
                """)
                existing_result = db.session.execute(existing_query, {
                    'student_id': student_id,
                    'date': today
                })
                
                if existing_result.fetchone()[0] == 0:
                    # Insert new progress record
                    insert_query = text("""
                        INSERT INTO student_progress 
                        (student_id, date, credits_completed, courses_in_progress,
                         academic_standing, graduation_progress, gpa, semester, year, created_at)
                        VALUES (:student_id, :date, :credits_completed, :courses_in_progress,
                                :academic_standing, :graduation_progress, :gpa, :semester, :year, :created_at)
                    """)
                    
                    db.session.execute(insert_query, {
                        'student_id': student_id,
                        'date': today,
                        'credits_completed': credits_completed,
                        'courses_in_progress': courses_in_progress,
                        'academic_standing': academic_standing,
                        'graduation_progress': graduation_progress,
                        'gpa': current_gpa,
                        'semester': semester,
                        'year': year,
                        'created_at': datetime.now()
                    })
                    
                    updated_count += 1
                    print(f"  Progress updated for {student_name}: {academic_standing}, {graduation_progress}% complete")
            
            db.session.commit()
            print(f"Student progress updated: {updated_count} students")
            
        except Exception as e:
            print(f"Error updating student progress: {e}")
            db.session.rollback()
    
    def update_student_statistics(self):
        """Update student statistics"""
        try:
            print("Updating student statistics...")
            
            today = date.today()
            
            # Calculate daily statistics
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_students,
                    AVG(gpa) as avg_gpa,
                    SUM(CASE WHEN gpa >= 8.0 THEN 1 ELSE 0 END) as high_performers,
                    SUM(CASE WHEN gpa >= 6.0 AND gpa < 8.0 THEN 1 ELSE 0 END) as average_performers,
                    SUM(CASE WHEN gpa < 6.0 THEN 1 ELSE 0 END) as low_performers,
                    MAX(gpa) as max_gpa,
                    MIN(gpa) as min_gpa
                FROM students
                WHERE gpa IS NOT NULL
            """)
            
            result = db.session.execute(stats_query)
            stats = result.fetchone()
            
            if stats and stats[0] > 0:
                # Store in daily statistics table
                insert_query = text("""
                    INSERT INTO student_daily_statistics 
                    (date, total_students, avg_gpa, high_performers, average_performers, 
                     low_performers, max_gpa, min_gpa, created_at)
                    VALUES (:date, :total_students, :avg_gpa, :high_performers, :average_performers,
                            :low_performers, :max_gpa, :min_gpa, :created_at)
                """)
                
                db.session.execute(insert_query, {
                    'date': today,
                    'total_students': stats[0],
                    'avg_gpa': round(stats[1] or 0, 2),
                    'high_performers': stats[2],
                    'average_performers': stats[3],
                    'low_performers': stats[4],
                    'max_gpa': stats[5] or 0,
                    'min_gpa': stats[6] or 0,
                    'created_at': datetime.now()
                })
                
                db.session.commit()
                
                print(f"Student Statistics for {today}:")
                print(f"  Total Students: {stats[0]}")
                print(f"  Average GPA: {stats[1]:.2f}")
                print(f"  High Performers: {stats[2]}")
                print(f"  Average Performers: {stats[3]}")
                print(f"  Low Performers: {stats[4]}")
                print(f"  GPA Range: {stats[6]:.2f} - {stats[5]:.2f}")
            
        except Exception as e:
            print(f"Error updating student statistics: {e}")
            db.session.rollback()
    
    def generate_student_reports(self):
        """Generate daily student reports"""
        try:
            print("Generating student reports...")
            
            today = date.today()
            
            # Get today's data summary
            performance_query = text("""
                SELECT COUNT(*) as total_performance_records
                FROM student_performance 
                WHERE date = :date
            """)
            
            activities_query = text("""
                SELECT COUNT(*) as total_activity_records,
                       SUM(library_visits) as total_library_visits,
                       SUM(lab_sessions) as total_lab_sessions
                FROM student_activities 
                WHERE date = :date
            """)
            
            progress_query = text("""
                SELECT COUNT(*) as total_progress_records,
                       AVG(graduation_progress) as avg_graduation_progress
                FROM student_progress 
                WHERE date = :date
            """)
            
            perf_result = db.session.execute(performance_query, {'date': today})
            act_result = db.session.execute(activities_query, {'date': today})
            prog_result = db.session.execute(progress_query, {'date': today})
            
            perf_stats = perf_result.fetchone()
            act_stats = act_result.fetchone()
            prog_stats = prog_result.fetchone()
            
            # Generate report summary
            avg_progress = prog_stats[1] if prog_stats and prog_stats[1] else 0
            report_summary = f"""
            Daily Student Report for {today}:
            - Performance Records: {perf_stats[0] if perf_stats else 0}
            - Activity Records: {act_stats[0] if act_stats else 0}
            - Progress Records: {prog_stats[0] if prog_stats else 0}
            - Total Library Visits: {act_stats[1] if act_stats else 0}
            - Total Lab Sessions: {act_stats[2] if act_stats else 0}
            - Average Graduation Progress: {avg_progress:.1f}%
            """
            
            print(report_summary)
            
        except Exception as e:
            print(f"Error generating student reports: {e}")
    
    def _generate_study_hours(self, gpa):
        """Generate study hours based on GPA"""
        if gpa >= 8.0:
            return random.randint(6, 10)
        elif gpa >= 7.0:
            return random.randint(4, 8)
        elif gpa >= 6.0:
            return random.randint(3, 6)
        else:
            return random.randint(1, 4)
    
    def _generate_assignment_completion(self, gpa):
        """Generate assignment completion rate based on GPA"""
        if gpa >= 8.0:
            return random.randint(85, 100)
        elif gpa >= 7.0:
            return random.randint(70, 90)
        elif gpa >= 6.0:
            return random.randint(50, 80)
        else:
            return random.randint(30, 60)
    
    def _generate_class_participation(self, gpa):
        """Generate class participation based on GPA"""
        if gpa >= 8.0:
            return random.randint(80, 95)
        elif gpa >= 7.0:
            return random.randint(60, 85)
        elif gpa >= 6.0:
            return random.randint(40, 70)
        else:
            return random.randint(20, 50)
    
    def _generate_test_performance(self, gpa):
        """Generate test performance based on GPA"""
        # Add some variation to current GPA
        variation = random.uniform(-0.3, 0.3)
        new_gpa = max(0.0, min(10.0, gpa + variation))
        return round(new_gpa, 2)
    
    def _calculate_gpa_trend(self, current_gpa, test_performance):
        """Calculate GPA trend"""
        if test_performance > current_gpa:
            return 'improving'
        elif test_performance < current_gpa:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_credits_completed(self, year, semester):
        """Calculate credits completed"""
        base_credits = (year - 1) * 40
        semester_credits = (semester - 1) * 20
        return base_credits + semester_credits + random.randint(15, 25)
    
    def _calculate_courses_in_progress(self, semester):
        """Calculate courses in progress"""
        return random.randint(4, 6)
    
    def _calculate_academic_standing(self, gpa):
        """Calculate academic standing"""
        if gpa >= 8.0:
            return 'Excellent'
        elif gpa >= 7.0:
            return 'Good'
        elif gpa >= 6.0:
            return 'Average'
        elif gpa >= 5.0:
            return 'Below Average'
        else:
            return 'Poor'
    
    def _calculate_graduation_progress(self, year, semester):
        """Calculate graduation progress"""
        total_semesters = 8  # 4 years * 2 semesters
        current_semester = (year - 1) * 2 + semester
        progress = (current_semester / total_semesters) * 100
        return round(progress, 1)
    
    def manual_update_now(self):
        """Force manual update now"""
        try:
            with self.app.app_context():
                print("Running manual student data update...")
                
                self.update_student_performance()
                self.update_student_activities()
                self.update_student_progress()
                self.update_student_statistics()
                self.generate_student_reports()
                
                print("Manual student data update completed")
                
        except Exception as e:
            print(f"Error in manual update: {e}")
    
    def get_student_data_status(self):
        """Get current student data status"""
        try:
            with self.app.app_context():
                today = date.today()
                
                # Performance data
                perf_query = text("""
                    SELECT COUNT(*) as total,
                           AVG(test_performance) as avg_performance
                    FROM student_performance 
                    WHERE date = :date
                """)
                
                # Activity data
                act_query = text("""
                    SELECT COUNT(*) as total,
                           SUM(library_visits) as total_library,
                           SUM(lab_sessions) as total_labs
                    FROM student_activities 
                    WHERE date = :date
                """)
                
                # Progress data
                prog_query = text("""
                    SELECT COUNT(*) as total,
                           AVG(graduation_progress) as avg_progress
                    FROM student_progress 
                    WHERE date = :date
                """)
                
                perf_result = db.session.execute(perf_query, {'date': today})
                act_result = db.session.execute(act_query, {'date': today})
                prog_result = db.session.execute(prog_query, {'date': today})
                
                perf_stats = perf_result.fetchone()
                act_stats = act_result.fetchone()
                prog_stats = prog_result.fetchone()
                
                return {
                    'date': today,
                    'performance': {
                        'total_records': perf_stats[0] if perf_stats else 0,
                        'avg_performance': perf_stats[1] if perf_stats else 0
                    },
                    'activities': {
                        'total_records': act_stats[0] if act_stats else 0,
                        'total_library_visits': act_stats[1] if act_stats else 0,
                        'total_lab_sessions': act_stats[2] if act_stats else 0
                    },
                    'progress': {
                        'total_records': prog_stats[0] if prog_stats else 0,
                        'avg_graduation_progress': prog_stats[1] if prog_stats else 0
                    },
                    'system_running': self.running
                }
                
        except Exception as e:
            print(f"Error getting status: {e}")
            return {'system_running': self.running}

# Global instance
student_data_system = DailyStudentDataSystem()

def start_student_data_system():
    """Start student data system"""
    student_data_system.start_system()

def stop_student_data_system():
    """Stop student data system"""
    student_data_system.stop_system()

def manual_student_data_update():
    """Force manual student data update"""
    student_data_system.manual_update_now()

def get_student_data_status():
    """Get current student data status"""
    return student_data_system.get_student_data_status()

if __name__ == '__main__':
    # Test the student data system
    print("Testing Daily Student Data System...")
    
    # Run manual update
    manual_student_data_update()
    
    # Show status
    status = get_student_data_status()
    print(f"Student Data Status: {status}")
    
    # Start automatic updates (optional)
    print("Starting automatic student data updates...")
    start_student_data_system()
    
    # Keep running for testing
    try:
        while True:
            time.sleep(60)
            status = get_student_data_status()
            print(f"System running: {status.get('system_running', False)}")
    except KeyboardInterrupt:
        print("Stopping system...")
        stop_student_data_system()
