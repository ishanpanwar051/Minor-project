"""
Create the Correct Users for Login Testing
"""

from app import create_app
from models import db, User

def create_login_users():
    """Create users with the correct credentials"""
    app = create_app()
    
    with app.app_context():
        # Create teacher user with correct credentials
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
        
        # Create student user with correct credentials
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
            print("🎉 Login users created successfully!")
            
            # Test the credentials
            print("\n🔑 Testing Login Credentials:")
            
            # Test teacher login
            teacher = User.query.filter_by(email='teacher@eduguard.com').first()
            if teacher and teacher.check_password('Teacher123!'):
                print("  ✅ Teacher login works: teacher@eduguard.com / Teacher123!")
            else:
                print("  ❌ Teacher login failed")
            
            # Test student login
            student = User.query.filter_by(email='student@eduguard.com').first()
            if student and student.check_password('Student123!'):
                print("  ✅ Student login works: student@eduguard.com / Student123!")
            else:
                print("  ❌ Student login failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_login_users()
