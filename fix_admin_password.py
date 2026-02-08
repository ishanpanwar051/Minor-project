from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("Current Users:")
    users = User.query.all()
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}, Role: {u.role}, Hash: {u.password_hash[:20]}...")

    print("\nResetting Admin Password...")
    admin = User.query.filter_by(email='admin@eduguard.edu').first()
    if not admin:
        print("Admin with email admin@eduguard.edu not found. Searching by username 'admin'...")
        admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f"Found admin user: {admin.username} ({admin.email})")
        # Use set_password method if available, or generate_password_hash directly
        if hasattr(admin, 'set_password'):
            admin.set_password('admin123')
            print("Password set using set_password()")
        else:
            admin.password_hash = generate_password_hash('admin123')
            print("Password set using generate_password_hash()")
        
        db.session.commit()
        print("✅ Admin password reset to: admin123")
    else:
        print("❌ Admin user not found. Creating new admin...")
        admin = User(
            username='admin',
            email='admin@eduguard.edu',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        try:
            db.session.commit()
            print("✅ Created new admin user: admin / admin123")
        except Exception as e:
            print(f"❌ Error creating admin: {e}")

