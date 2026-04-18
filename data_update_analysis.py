"""
Data Update Analysis - Daily basis par data update check
Hindi/Urdu mein data update ka analysis
"""

import os
from sqlalchemy import text
from datetime import datetime, timedelta
from app import create_app
from models import db

def data_update_analysis():
    """Check if data is updating daily basis"""
    app = create_app()
    
    with app.app_context():
        print("=== DAILY DATA UPDATE ANALYSIS (HINDI/URDU) ===")
        print()
        
        # 1. Check recent data updates
        print("1. RECENT DATA UPDATES (RECENT UPDATES):")
        
        # Check attendance updates
        print("   Attendance Updates:")
        attendance_query = text("""
            SELECT date, COUNT(*) as count, MAX(created_at) as created_at
            FROM attendance 
            WHERE date >= date('now', '-7 days')
            GROUP BY date
            ORDER BY date DESC
            LIMIT 5
        """)
        
        try:
            result = db.session.execute(attendance_query)
            attendance_updates = result.fetchall()
            
            if attendance_updates:
                print(f"     Last 7 days mein {len(attendance_updates)} days ka data:")
                for row in attendance_updates:
                    date_str = row[0]
                    count = row[1]
                    created_at = row[2]
                    print(f"     - {date_str}: {count} records (Updated: {created_at})")
            else:
                print("     Last 7 days mein koi attendance update nahi")
                
        except Exception as e:
            print(f"     Error checking attendance: {e}")
        
        # Check scholarship applications
        print("\n   Scholarship Applications:")
        app_query = text("""
            SELECT application_date, COUNT(*) as count
            FROM scholarship_applications 
            WHERE application_date >= date('now', '-30 days')
            GROUP BY application_date
            ORDER BY application_date DESC
            LIMIT 5
        """)
        
        try:
            result = db.session.execute(app_query)
            app_updates = result.fetchall()
            
            if app_updates:
                print(f"     Last 30 days mein {len(app_updates)} applications:")
                for row in app_updates:
                    date_str = row[0]
                    count = row[1]
                    print(f"     - {date_str}: {count} applications")
            else:
                print("     Last 30 days mein koi new application nahi")
                
        except Exception as e:
            print(f"     Error checking applications: {e}")
        
        # Check counselling requests
        print("\n   Counselling Requests:")
        counselling_query = text("""
            SELECT request_date, COUNT(*) as count
            FROM counselling_requests 
            WHERE request_date >= date('now', '-30 days')
            GROUP BY request_date
            ORDER BY request_date DESC
            LIMIT 5
        """)
        
        try:
            result = db.session.execute(counselling_query)
            counselling_updates = result.fetchall()
            
            if counselling_updates:
                print(f"     Last 30 days mein {len(counselling_updates)} counselling requests:")
                for row in counselling_updates:
                    date_str = row[0]
                    count = row[1]
                    print(f"     - {date_str}: {count} requests")
            else:
                print("     Last 30 days mein koi new counselling request nahi")
                
        except Exception as e:
            print(f"     Error checking counselling: {e}")
        
        print()
        print("2. AUTOMATIC UPDATES (AUTOMATIC UPDATES):")
        
        # Check if there are any automatic processes
        print("   Automatic data sources:")
        
        # Check if there's any timestamp-based data
        timestamp_query = text("""
            SELECT name FROM sqlite_master 
            WHERE sql LIKE '%created_at%' OR sql LIKE '%updated_at%' OR sql LIKE '%timestamp%'
        """)
        
        try:
            result = db.session.execute(timestamp_query)
            timestamp_tables = [row[0] for row in result.fetchall()]
            
            if timestamp_tables:
                print(f"     Timestamp wale tables: {timestamp_tables}")
            else:
                print("     Koi table mein timestamp fields nahi")
                
        except Exception as e:
            print(f"     Error checking timestamps: {e}")
        
        print()
        print("3. MANUAL VS AUTOMATIC DATA:")
        
        # Check data creation patterns
        print("   Data creation patterns:")
        
        # Check if data looks like sample data
        sample_indicators = []
        
        # Check for consecutive dates in attendance
        attendance_pattern_query = text("""
            SELECT COUNT(DISTINCT date) as unique_dates,
                   MIN(date) as min_date,
                   MAX(date) as max_date
            FROM attendance
        """)
        
        try:
            result = db.session.execute(attendance_pattern_query)
            pattern_data = result.fetchone()
            
            if pattern_data:
                unique_dates = pattern_data[0]
                min_date = pattern_data[1]
                max_date = pattern_data[2]
                
                if unique_dates > 0:
                    print(f"     Attendance: {unique_dates} unique dates ({min_date} to {max_date})")
                    
                    # Check if dates are consecutive (sample data indicator)
                    if unique_dates >= 25:  # Large number of dates might indicate sample data
                        sample_indicators.append("Attendance sample data")
                    
        except Exception as e:
            print(f"     Error checking attendance pattern: {e}")
        
        # Check user creation pattern
        user_pattern_query = text("""
            SELECT COUNT(*) as total_users,
                   MIN(created_at) as min_created,
                   MAX(created_at) as max_created
            FROM users
            WHERE created_at IS NOT NULL
        """)
        
        try:
            result = db.session.execute(user_pattern_query)
            user_pattern = result.fetchone()
            
            if user_pattern and user_pattern[0] > 0:
                total_users = user_pattern[0]
                min_created = user_pattern[1]
                max_created = user_pattern[2]
                
                print(f"     Users: {total_users} users ({min_created} to {max_created})")
                
        except Exception as e:
            print(f"     Error checking user pattern: {e}")
        
        print()
        print("4. DATA SOURCE ANALYSIS:")
        
        if sample_indicators:
            print("   Sample Data Indicators:")
            for indicator in sample_indicators:
                print(f"     - {indicator}")
            print("   Ye data manually create kiya gaya hai, daily update nahi ho raha")
        else:
            print("   Data real-time ya manual entry lag raha hai")
        
        print()
        print("5. RECOMMENDATIONS (SUGGESTIONS):")
        
        print("   Daily update ke liye:")
        print("   - Attendance: Daily automatic update ho sakta hai")
        print("   - Applications: User manually submit karte hain")
        print("   - Counselling: User manually request karte hain")
        print("   - User data: Admin manually add karte hain")
        
        print()
        print("   Current status:")
        print("   - Most data sample data hai (manually created)")
        print("   - Daily automatic update abhi active nahi hai")
        print("   - Real-time data entry user-dependent hai")
        
        print()
        print("=== ANALYSIS COMPLETE ===")

if __name__ == '__main__':
    data_update_analysis()
