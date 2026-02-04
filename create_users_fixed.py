"""
Create Default Users for EduGuard System - Fixed Version
"""

from app import create_app
from models import db, User

def create_default_users():
    """Create default admin, teacher, and student users"""
    app = create_app()
    
    with app.app_context():
        # Create default admin user
        admin = User.query.filter_by(email='admin@eduguard.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@eduguard.com',
                role='admin'
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            print("✅ Created admin user: admin@eduguard.com / Admin123!")
        else:
            print("ℹ️ Admin user already exists")
        
        # Create default teacher user
        teacher = User.query.filter_by(email='teacher@eduguard.com').first()
        if not teacher:
            teacher = User(
                username='teacher',
                email='teacher@eduguard.com',
                role='faculty'
            )
            teacher.set_password('Teacher123!')
            db.session.add(teacher)
            print("✅ Created teacher user: teacher@eduguard.com / Teacher123!")
        else:
            print("ℹ️ Teacher user already exists")
        
        # Create default student user
        student = User.query.filter_by(email='student@eduguard.com').first()
        if not student:
            student = User(
                username='student',
                email='student@eduguard.com',
                role='student'
            )
            student.set_password('Student123!')
            db.session.add(student)
            print("✅ Created student user: student@eduguard.com / Student123!")
        else:
            print("ℹ️ Student user already exists")
        
        try:
            db.session.commit()
            print("🎉 Default users created successfully!")
            
            # List all users
            users = User.query.all()
            print("\n📋 Current Users:")
            for user in users:
                print(f"  - {user.email} ({user.role})")
        except Exception as e:
            print(f"❌ Error committing to database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_default_users()
