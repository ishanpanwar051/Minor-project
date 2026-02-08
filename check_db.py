from app import create_app
from models import db, User, Student, Attendance, RiskProfile

app = create_app()

with app.app_context():
    print("Checking database tables...")
    try:
        users = User.query.all()
        print(f"Users: {len(users)}")
        
        students = Student.query.all()
        print(f"Students: {len(students)}")
        
        attendance = Attendance.query.all()
        print(f"Attendance records: {len(attendance)}")
        
        risk_profiles = RiskProfile.query.all()
        print(f"Risk Profiles: {len(risk_profiles)}")
        
        print("✅ Database check passed")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback
        traceback.print_exc()
