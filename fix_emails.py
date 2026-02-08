from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    # Fix Admin
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.email = 'admin@eduguard.edu'
        print(f"✅ Updated admin email to {admin.email}")
    
    # Fix Faculty (let's pick one to be the main demo faculty)
    faculty = User.query.filter_by(role='faculty').first()
    if faculty:
        faculty.email = 'faculty@eduguard.edu'
        # Reset password to match demo
        if hasattr(faculty, 'set_password'):
            faculty.set_password('faculty123')
        print(f"✅ Updated faculty {faculty.username} email to {faculty.email} and password to faculty123")
        
    db.session.commit()
    print("✅ Database updated successfully")
