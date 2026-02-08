from app import create_app
from models import User
import sys

def verify_login():
    app = create_app()
    with app.app_context():
        # Test Admin
        user = User.query.filter_by(email='admin@eduguard.edu').first()
        if user and user.check_password('admin123'):
            print("✅ Admin login verification SUCCESS")
        else:
            print("❌ Admin login verification FAILED")
            if user:
                print(f"   User found, password hash: {user.password_hash[:20]}...")
            else:
                print("   User not found")

        # Test Faculty
        user = User.query.filter_by(email='faculty@eduguard.edu').first()
        if user and user.check_password('faculty123'):
            print("✅ Faculty login verification SUCCESS")
        else:
            print("❌ Faculty login verification FAILED")

        # Test Student
        user = User.query.filter_by(email='john.doe@eduguard.edu').first()
        if user and user.check_password('student123'):
            print("✅ Student login verification SUCCESS")
        else:
            print("❌ Student login verification FAILED")

if __name__ == "__main__":
    verify_login()