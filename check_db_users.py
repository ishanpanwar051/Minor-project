"""
Check Database Users
Verify what users exist in the database
"""

from eduguard_final import app, db, User

def check_users():
    """Check what users exist in database"""
    with app.app_context():
        users = User.query.all()
        print("📋 USERS IN DATABASE:")
        print("=" * 50)
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Password Hash: {user.password_hash}")
            print("-" * 30)
        
        if not users:
            print("❌ NO USERS FOUND IN DATABASE")
        else:
            print(f"✅ Found {len(users)} users")

if __name__ == '__main__':
    check_users()
