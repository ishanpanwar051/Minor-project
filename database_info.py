"""
Database Information and Storage Details
Hindi/Urdu mein database ka location aur storage info
"""

import os
from sqlalchemy import text
from app import create_app
from models import db

def database_info():
    """Database ka complete information"""
    app = create_app()
    
    with app.app_context():
        print("=== DATABASE INFORMATION (HINDI/URDU) ===")
        print()
        
        # Database location
        print("1. DATABASE LOCATION (KAHAN HAI):")
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///eduguard.db')
        print(f"   Database Path: {db_path}")
        
        if 'sqlite' in db_path:
            # Extract file path from sqlite URI
            if db_path.startswith('sqlite:///'):
                file_path = db_path[10:]  # Remove 'sqlite:///'
                full_path = os.path.abspath(file_path)
                print(f"   Full Path: {full_path}")
                
                # Check if file exists
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    print(f"   File Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
                    print(f"   File Exists: Haan, file mojood hai")
                else:
                    print(f"   File Exists: Nahi, file nahi hai")
        
        print()
        print("2. STORAGE DETAILS (SAAB KUCH KAHAN STORE HAI):")
        
        # Check all tables
        tables_query = text("SELECT name FROM sqlite_master WHERE type='table'")
        result = db.session.execute(tables_query)
        tables = [row[0] for row in result.fetchall()]
        
        print(f"   Total Tables: {len(tables)}")
        print("   Tables ki list:")
        
        for table in sorted(tables):
            # Count records in each table
            count_query = text(f"SELECT COUNT(*) FROM {table}")
            count_result = db.session.execute(count_query)
            record_count = count_result.fetchone()[0]
            
            print(f"   - {table}: {record_count:,} records")
        
        print()
        print("3. IMPORTANT DATA (ZAROORI DATA):")
        
        # Check key tables
        key_tables = ['users', 'students', 'scholarships', 'scholarship_applications', 'counselling_requests', 'attendance']
        
        for table in key_tables:
            if table in tables:
                count_query = text(f"SELECT COUNT(*) FROM {table}")
                count_result = db.session.execute(count_query)
                record_count = count_result.fetchone()[0]
                
                if record_count > 0:
                    print(f"   - {table}: {record_count} records (Data hai)")
                    
                    # Show some sample data
                    if table == 'users':
                        sample_query = text(f"SELECT email, role FROM {table} LIMIT 3")
                        sample_result = db.session.execute(sample_query)
                        samples = sample_result.fetchall()
                        print(f"     Sample: {[f'{row[0]} ({row[1]})' for row in samples]}")
                    
                    elif table == 'students':
                        sample_query = text(f"SELECT first_name, last_name, email, gpa FROM {table} LIMIT 3")
                        sample_result = db.session.execute(sample_query)
                        samples = sample_result.fetchall()
                        print(f"     Sample: {[f'{row[0]} {row[1]} (GPA: {row[3]})' for row in samples]}")
                    
                    elif table == 'scholarships':
                        sample_query = text(f"SELECT title, amount, status FROM {table} LIMIT 3")
                        sample_result = db.session.execute(sample_query)
                        samples = sample_result.fetchall()
                        print(f"     Sample: {[f'{row[0]} (${row[1]})' for row in samples]}")
                        
                else:
                    print(f"   - {table}: 0 records (Khaali hai)")
        
        print()
        print("4. FILE SYSTEM INFO:")
        current_dir = os.getcwd()
        print(f"   Current Directory: {current_dir}")
        
        # Check for database file
        if 'sqlite' in db_path and db_path.startswith('sqlite:///'):
            file_path = db_path[10:]
            full_path = os.path.abspath(file_path)
            print(f"   Database File: {full_path}")
            
            # Check directory
            db_dir = os.path.dirname(full_path)
            print(f"   Database Directory: {db_dir}")
            
            # List files in directory
            if os.path.exists(db_dir):
                files = os.listdir(db_dir)
                db_files = [f for f in files if f.endswith('.db') or f.endswith('.sqlite')]
                print(f"   Database files in directory: {db_files}")
        
        print()
        print("5. BACKUP & EXPORT INFO:")
        print("   Database backup ke liye:")
        print("   - SQLite file ko copy kar sakte hain")
        print("   - Export kar sakte hain SQL format mein")
        print("   - CSV export bhi possible hai")
        
        print()
        print("=== COMPLETE INFO ===")

if __name__ == '__main__':
    database_info()
