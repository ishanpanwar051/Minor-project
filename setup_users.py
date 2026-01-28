"""
EduGuard Login Guide - Default Users

This script creates default users for testing the EduGuard system.
Run this script to create admin, teacher, and student accounts.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os

def create_default_users():
    """Create default users for testing"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduguard_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Simple User model for creation
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(64), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        role = db.Column(db.String(20), default='faculty')
        is_active = db.Column(db.Boolean, default=True)
        
        def set_password(self, password):
            self.password_hash = generate_password_hash(password)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin user
        admin = User.query.filter_by(email='admin@eduguard.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@eduguard.com',
                role='admin'
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            print("Admin user created:")
            print("   Email: admin@eduguard.com")
            print("   Password: Admin123!")
        
        # Create teacher user
        teacher = User.query.filter_by(email='teacher@eduguard.com').first()
        if not teacher:
            teacher = User(
                username='teacher',
                email='teacher@eduguard.com',
                role='faculty'
            )
            teacher.set_password('Teacher123!')
            db.session.add(teacher)
            print("Teacher user created:")
            print("   Email: teacher@eduguard.com")
            print("   Password: Teacher123!")
        
        # Create student user
        student = User.query.filter_by(email='student@eduguard.com').first()
        if not student:
            student = User(
                username='student',
                email='student@eduguard.com',
                role='student'
            )
            student.set_password('Student123!')
            db.session.add(student)
            print("Student user created:")
            print("   Email: student@eduguard.com")
            print("   Password: Student123!")
        
        db.session.commit()
        print("\nDefault users created successfully!")
        print("\nLogin Credentials:")
        print("=" * 50)
        print("ADMIN LOGIN:")
        print("   Email: admin@eduguard.com")
        print("   Password: Admin123!")
        print("   Access: Full system access")
        print("")
        print("TEACHER LOGIN:")
        print("   Email: teacher@eduguard.com")
        print("   Password: Teacher123!")
        print("   Access: Student management, analytics")
        print("")
        print("STUDENT LOGIN:")
        print("   Email: student@eduguard.com")
        print("   Password: Student123!")
        print("   Access: Personal dashboard only")
        print("=" * 50)

if __name__ == '__main__':
    create_default_users()
