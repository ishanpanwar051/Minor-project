"""
Debug Admin Login Issue for EduGuard System
"""

import sqlite3
import hashlib

def debug_admin_login():
    """Debug admin login issue"""
    try:
        # Connect to database
        conn = sqlite3.connect('eduguard.db')
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE email = ?", ('admin@university.edu',))
        admin_user = cursor.fetchone()
        
        if admin_user:
            print("✅ Admin user found in database:")
            print(f"   ID: {admin_user[0]}")
            print(f"   Username: {admin_user[1]}")
            print(f"   Email: {admin_user[2]}")
            print(f"   Role: {admin_user[4]}")
            print(f"   Created: {admin_user[5]}")
            
            # Test password hash
            stored_hash = admin_user[3]
            test_password = "admin123"
            test_hash = hashlib.sha256(test_password.encode()).hexdigest()
            
            print(f"\n🔐 Password Verification:")
            print(f"   Stored Hash: {stored_hash}")
            print(f"   Test Hash: {test_hash}")
            print(f"   Hashes Match: {stored_hash == test_hash}")
            
            if stored_hash != test_hash:
                print("❌ Password hash mismatch! Updating admin password...")
                new_hash = hashlib.sha256('admin123'.encode()).hexdigest()
                cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", 
                             (new_hash, 'admin@university.edu'))
                conn.commit()
                print("✅ Admin password updated successfully!")
            
        else:
            print("❌ Admin user not found in database!")
            print("Creating admin user...")
            
            # Create admin user
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role) 
                VALUES (?, ?, ?, ?)
            """, ('admin', 'admin@university.edu', password_hash, 'admin'))
            
            conn.commit()
            print("✅ Admin user created successfully!")
        
        conn.close()
        
        print("\n🔐 ADMIN LOGIN CREDENTIALS:")
        print("=" * 40)
        print("Email: admin@university.edu")
        print("Password: admin123")
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    debug_admin_login()
