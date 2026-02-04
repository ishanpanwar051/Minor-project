"""
Create Admin User for EduGuard System
"""

from app import create_app
from models import db, User

def create_admin_user():
    """Create admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@eduguard.com').first()
        if admin:
            print("ℹ️ Admin user already exists")
        else:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@eduguard.com',
                role='admin'
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()
            print("✅ Created admin user: admin@eduguard.com / Admin123!")
        
        # Verify admin login
        admin = User.query.filter_by(email='admin@eduguard.com').first()
        if admin and admin.check_password('Admin123!'):
            print("✅ Admin login verified: admin@eduguard.com / Admin123!")
        else:
            print("❌ Admin login failed")
        
        # List all users
        users = User.query.all()
        print("\n📋 All Users in System:")
        for user in users:
            print(f"  - {user.email} ({user.role})")

if __name__ == '__main__':
    create_admin_user()
