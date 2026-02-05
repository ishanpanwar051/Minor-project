"""
Test Password Verification
Check if passwords are being verified correctly
"""

from eduguard_final import app, db, User
import hashlib

def test_passwords():
    """Test password verification"""
    with app.app_context():
        users = User.query.all()
        print("🔐 TESTING PASSWORD VERIFICATION:")
        print("=" * 50)
        
        test_passwords = [
            ("admin@eduguard.edu", "admin123"),
            ("faculty@eduguard.edu", "faculty123"),
            ("john.doe@eduguard.edu", "student123")
        ]
        
        for email, password in test_passwords:
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"\n👤 User: {user.email}")
                print(f"🔑 Testing password: {password}")
                print(f"📝 Stored hash: {user.password_hash}")
                
                # Test SHA256 hash
                sha256_hash = hashlib.sha256(password.encode()).hexdigest()
                print(f"🔢 SHA256 hash: {sha256_hash}")
                print(f"✅ SHA256 match: {sha256_hash == user.password_hash}")
                
                # Test user.check_password method
                try:
                    password_check = user.check_password(password)
                    print(f"🔍 check_password result: {password_check}")
                except Exception as e:
                    print(f"❌ check_password error: {e}")
                
                print("-" * 40)

if __name__ == '__main__':
    test_passwords()
