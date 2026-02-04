"""
Check Existing Users and Test Login
"""

from app import create_app
from models import db, User

def check_users():
    """Check existing users in database"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        print("📋 Existing Users in Database:")
        if not users:
            print("  No users found in database")
        else:
            for user in users:
                print(f"  - {user.email} ({user.username}) - Role: {user.role}")
        
        # Test login credentials
        print("\n🔑 Testing Login Credentials:")
        
        # Test admin login
        admin = User.query.filter_by(email='admin@eduguard.com').first()
        if admin:
            if admin.check_password('Admin123!'):
                print("  ✅ Admin login works: admin@eduguard.com / Admin123!")
            else:
                print("  ❌ Admin login failed: admin@eduguard.com / Admin123!")
        else:
            print("  ❌ Admin user not found")
        
        # Test teacher login
        teacher = User.query.filter_by(email='teacher@eduguard.com').first()
        if teacher:
            if teacher.check_password('Teacher123!'):
                print("  ✅ Teacher login works: teacher@eduguard.com / Teacher123!")
            else:
                print("  ❌ Teacher login failed: teacher@eduguard.com / Teacher123!")
        else:
            print("  ❌ Teacher user not found")
        
        # Test student login
        student = User.query.filter_by(email='student@eduguard.com').first()
        if student:
            if student.check_password('Student123!'):
                print("  ✅ Student login works: student@eduguard.com / Student123!")
            else:
                print("  ❌ Student login failed: student@eduguard.com / Student123!")
        else:
            print("  ❌ Student user not found")

if __name__ == '__main__':
    check_users()
