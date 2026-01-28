from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from models_new import User, UserRole
import os

def create_default_users():
    """Create default users for testing"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduguard_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin user
        admin = User.query.filter_by(email='admin@eduguard.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@eduguard.com',
                role=UserRole.ADMIN
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            print("✅ Admin user created:")
            print("   Email: admin@eduguard.com")
            print("   Password: Admin123!")
        
        # Create teacher user
        teacher = User.query.filter_by(email='teacher@eduguard.com').first()
        if not teacher:
            teacher = User(
                username='teacher',
                email='teacher@eduguard.com',
                role=UserRole.TEACHER
            )
            teacher.set_password('Teacher123!')
            db.session.add(teacher)
            print("✅ Teacher user created:")
            print("   Email: teacher@eduguard.com")
            print("   Password: Teacher123!")
        
        # Create student user
        student = User.query.filter_by(email='student@eduguard.com').first()
        if not student:
            student = User(
                username='student',
                email='student@eduguard.com',
                role=UserRole.STUDENT
            )
            student.set_password('Student123!')
            db.session.add(student)
            print("✅ Student user created:")
            print("   Email: student@eduguard.com")
            print("   Password: Student123!")
        
        db.session.commit()
        print("\n🎉 Default users created successfully!")

if __name__ == '__main__':
    create_default_users()
