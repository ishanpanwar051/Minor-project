"""
Setup Student Data Tables
Create tables for daily student data updates
"""

from sqlalchemy import text
from app import create_app
from models import db

def setup_student_data_tables():
    """Create student data tables"""
    app = create_app()
    
    with app.app_context():
        print("Setting up Student Data Tables...")
        
        try:
            # Create student_performance table
            create_performance_query = text("""
                CREATE TABLE IF NOT EXISTS student_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    study_hours REAL DEFAULT 0,
                    assignment_completion INTEGER DEFAULT 0,
                    class_participation INTEGER DEFAULT 0,
                    test_performance REAL DEFAULT 0,
                    gpa_trend VARCHAR(20) DEFAULT 'stable',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    UNIQUE(student_id, date)
                )
            """)
            
            db.session.execute(create_performance_query)
            print("Student performance table created/verified")
            
            # Create student_activities table
            create_activities_query = text("""
                CREATE TABLE IF NOT EXISTS student_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    library_visits INTEGER DEFAULT 0,
                    lab_sessions INTEGER DEFAULT 0,
                    sports_participation INTEGER DEFAULT 0,
                    extracurricular INTEGER DEFAULT 0,
                    online_courses INTEGER DEFAULT 0,
                    social_activities INTEGER DEFAULT 0,
                    community_service INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    UNIQUE(student_id, date)
                )
            """)
            
            db.session.execute(create_activities_query)
            print("Student activities table created/verified")
            
            # Create student_progress table
            create_progress_query = text("""
                CREATE TABLE IF NOT EXISTS student_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    credits_completed INTEGER DEFAULT 0,
                    courses_in_progress INTEGER DEFAULT 0,
                    academic_standing VARCHAR(20) DEFAULT 'Average',
                    graduation_progress REAL DEFAULT 0,
                    gpa REAL DEFAULT 0,
                    semester INTEGER DEFAULT 1,
                    year INTEGER DEFAULT 1,
                    rank_in_class INTEGER,
                    class_size INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    UNIQUE(student_id, date)
                )
            """)
            
            db.session.execute(create_progress_query)
            print("Student progress table created/verified")
            
            # Create student_daily_statistics table
            create_stats_query = text("""
                CREATE TABLE IF NOT EXISTS student_daily_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL UNIQUE,
                    total_students INTEGER DEFAULT 0,
                    avg_gpa REAL DEFAULT 0,
                    high_performers INTEGER DEFAULT 0,
                    average_performers INTEGER DEFAULT 0,
                    low_performers INTEGER DEFAULT 0,
                    max_gpa REAL DEFAULT 0,
                    min_gpa REAL DEFAULT 0,
                    total_study_hours REAL DEFAULT 0,
                    avg_assignment_completion REAL DEFAULT 0,
                    total_library_visits INTEGER DEFAULT 0,
                    total_lab_sessions INTEGER DEFAULT 0,
                    avg_graduation_progress REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            db.session.execute(create_stats_query)
            print("Student daily statistics table created/verified")
            
            # Create indexes for better performance
            create_indexes_query = text("""
                CREATE INDEX IF NOT EXISTS idx_student_performance_date ON student_performance(date);
                CREATE INDEX IF NOT EXISTS idx_student_performance_student ON student_performance(student_id);
                CREATE INDEX IF NOT EXISTS idx_student_activities_date ON student_activities(date);
                CREATE INDEX IF NOT EXISTS idx_student_activities_student ON student_activities(student_id);
                CREATE INDEX IF NOT EXISTS idx_student_progress_date ON student_progress(date);
                CREATE INDEX IF NOT EXISTS idx_student_progress_student ON student_progress(student_id);
                CREATE INDEX IF NOT EXISTS idx_student_stats_date ON student_daily_statistics(date);
            """)
            
            db.session.execute(create_indexes_query)
            print("Indexes created for performance")
            
            db.session.commit()
            print("Student data tables setup completed!")
            
        except Exception as e:
            print(f"Error setting up student data tables: {e}")
            db.session.rollback()

def test_student_data_tables():
    """Test student data tables"""
    app = create_app()
    
    with app.app_context():
        print("Testing Student Data Tables...")
        
        try:
            # Test student_performance table
            perf_query = text("SELECT COUNT(*) FROM student_performance")
            result = db.session.execute(perf_query)
            perf_count = result.fetchone()[0]
            print(f"Student Performance Records: {perf_count}")
            
            # Test student_activities table
            act_query = text("SELECT COUNT(*) FROM student_activities")
            result = db.session.execute(act_query)
            act_count = result.fetchone()[0]
            print(f"Student Activity Records: {act_count}")
            
            # Test student_progress table
            prog_query = text("SELECT COUNT(*) FROM student_progress")
            result = db.session.execute(prog_query)
            prog_count = result.fetchone()[0]
            print(f"Student Progress Records: {prog_count}")
            
            # Test student_daily_statistics table
            stats_query = text("SELECT COUNT(*) FROM student_daily_statistics")
            result = db.session.execute(stats_query)
            stats_count = result.fetchone()[0]
            print(f"Student Daily Statistics: {stats_count}")
            
            print("Student data tables test completed!")
            
        except Exception as e:
            print(f"Error testing student data tables: {e}")

if __name__ == '__main__':
    setup_student_data_tables()
    test_student_data_tables()
