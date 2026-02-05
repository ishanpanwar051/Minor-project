"""
Direct Admin User Creation for EduGuard System
"""

import sqlite3
from werkzeug.security import generate_password_hash

def create_admin_directly():
    """Create admin user directly in database"""
    try:
        # Connect to database
        conn = sqlite3.connect('eduguard.db')
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE email = ?", ('admin@university.edu',))
        existing_admin = cursor.fetchone()
        
        if not existing_admin:
            # Create admin user
            hashed_password = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role) 
                VALUES (?, ?, ?, ?)
            """, ('admin', 'admin@university.edu', hashed_password, 'admin'))
            
            conn.commit()
            print("✅ Admin user created successfully!")
        else:
            print("ℹ️ Admin user already exists")
        
        conn.close()
        
        print("\n🔐 ADMIN LOGIN CREDENTIALS:")
        print("=" * 40)
        print("Email: admin@university.edu")
        print("Password: admin123")
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")

if __name__ == '__main__':
    create_admin_directly()
