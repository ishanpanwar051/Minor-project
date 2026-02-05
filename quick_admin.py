"""
Simple Admin User Creation for EduGuard System
"""

import sqlite3
import hashlib

def create_admin_simple():
    """Create admin user with simple password hashing"""
    try:
        # Connect to database
        conn = sqlite3.connect('eduguard.db')
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE email = ?", ('admin@university.edu',))
        existing_admin = cursor.fetchone()
        
        if not existing_admin:
            # Simple password hash (for demo purposes)
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            
            # Create admin user
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role) 
                VALUES (?, ?, ?, ?)
            """, ('admin', 'admin@university.edu', password_hash, 'admin'))
            
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
        print("\n🌐 Go to: http://127.0.0.1:5000/login")
        print("📝 Use the credentials above to login as admin")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")

if __name__ == '__main__':
    create_admin_simple()
