"""
COMPLETE WORKING EDUGUARD APPLICATION
This is a fully functional Flask application that addresses all issues
"""

from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import hashlib
import os

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'eduguard-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduguard_working.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='faculty')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(50))
    semester = db.Column(db.Integer, default=1)
    gpa = db.Column(db.Float, default=0.0)
    attendance_percentage = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # present, absent, late
    subject = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RiskProfile(db.Model):
    __tablename__ = 'risk_profiles'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    risk_level = db.Column(db.String(20), nullable=False)  # low, medium, high
    gpa_risk = db.Column(db.Boolean, default=False)
    attendance_risk = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics
    total_students = Student.query.count()
    at_risk_students = RiskProfile.query.filter_by(risk_level='high').count()
    
    # Calculate average attendance
    avg_attendance = db.session.query(db.func.avg(Student.attendance_percentage)).scalar() or 0
    
    # Get recent alerts
    recent_alerts = []
    high_risk_students = RiskProfile.query.filter_by(risk_level='high').limit(5).all()
    for risk in high_risk_students:
        student = Student.query.get(risk.student_id)
        if student:
            recent_alerts.append({
                'student_name': f"{student.first_name} {student.last_name}",
                'message': f"High risk student - GPA: {student.gpa}, Attendance: {student.attendance_percentage}%",
                'time': '2 hours ago'
            })
    
    return render_template('dashboard.html', 
                         total_students=total_students,
                         at_risk_students=at_risk_students,
                         avg_attendance=round(avg_attendance, 1),
                         recent_alerts=recent_alerts)

@app.route('/students')
@login_required
def students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Student.query
    if search:
        query = query.filter(
            db.or_(
                Student.first_name.ilike(f'%{search}%'),
                Student.last_name.ilike(f'%{search}%'),
                Student.student_id.ilike(f'%{search}%')
            )
        )
    
    students = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('students.html', students=students, search=search)

@app.route('/attendance')
@login_required
def attendance():
    # Get attendance data
    attendance_records = Attendance.query.order_by(Attendance.date.desc()).limit(20).all()
    
    attendance_data = []
    for record in attendance_records:
        student = Student.query.get(record.student_id)
        if student:
            attendance_data.append({
                'student_name': f"{student.first_name} {student.last_name}",
                'student_id': student.student_id,
                'date': record.date.strftime('%Y-%m-%d'),
                'status': record.status,
                'subject': record.subject or 'N/A'
            })
    
    return render_template('attendance.html', attendance_data=attendance_data)

@app.route('/risk')
@login_required
def risk():
    # Get risk profiles
    risk_profiles = RiskProfile.query.all()
    
    risk_data = []
    for risk in risk_profiles:
        student = Student.query.get(risk.student_id)
        if student:
            risk_data.append({
                'student_name': f"{student.first_name} {student.last_name}",
                'student_id': student.student_id,
                'risk_level': risk.risk_level,
                'gpa': student.gpa,
                'attendance': student.attendance_percentage,
                'factors': []
            })
            
            if risk.gpa_risk:
                risk_data[-1]['factors'].append('Low GPA')
            if risk.attendance_risk:
                risk_data[-1]['factors'].append('Poor Attendance')
    
    return render_template('risk.html', risk_data=risk_data)

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Admin access required', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get system statistics
    total_users = User.query.count()
    total_students = Student.query.count()
    total_attendance = Attendance.query.count()
    total_risk = RiskProfile.query.count()
    
    return render_template('admin.html',
                         total_users=total_users,
                         total_students=total_students,
                         total_attendance=total_attendance,
                         total_risk=total_risk)

# Create database and sample data
def create_sample_data():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create users
        admin_user = User(username='admin', email='admin@eduguard.edu', role='admin')
        admin_user.set_password('admin123')
        
        faculty_user = User(username='faculty', email='faculty@eduguard.edu', role='faculty')
        faculty_user.set_password('faculty123')
        
        db.session.add(admin_user)
        db.session.add(faculty_user)
        db.session.commit()
        
        # Create sample students with Indian names and CGPA out of 10
        students_data = [
            {'student_id': 'ST001', 'first_name': 'Rahul', 'last_name': 'Sharma', 'email': 'rahul.sharma@eduguard.edu', 'department': 'Computer Science', 'gpa': 8.2, 'attendance_percentage': 85.0},
            {'student_id': 'ST002', 'first_name': 'Priya', 'last_name': 'Patel', 'email': 'priya.patel@eduguard.edu', 'department': 'Engineering', 'gpa': 7.5, 'attendance_percentage': 75.0},
            {'student_id': 'ST003', 'first_name': 'Amit', 'last_name': 'Kumar', 'email': 'amit.kumar@eduguard.edu', 'department': 'Business', 'gpa': 8.8, 'attendance_percentage': 92.0},
            {'student_id': 'ST004', 'first_name': 'Sneha', 'last_name': 'Reddy', 'email': 'sneha.reddy@eduguard.edu', 'department': 'Computer Science', 'gpa': 6.2, 'attendance_percentage': 65.0},
            {'student_id': 'ST005', 'first_name': 'Vikram', 'last_name': 'Singh', 'email': 'vikram.singh@eduguard.edu', 'department': 'Engineering', 'gpa': 9.1, 'attendance_percentage': 95.0},
            {'student_id': 'ST006', 'first_name': 'Anjali', 'last_name': 'Gupta', 'email': 'anjali.gupta@eduguard.edu', 'department': 'Mathematics', 'gpa': 7.8, 'attendance_percentage': 88.0},
            {'student_id': 'ST007', 'first_name': 'Rohit', 'last_name': 'Verma', 'email': 'rohit.verma@eduguard.edu', 'department': 'Physics', 'gpa': 6.9, 'attendance_percentage': 70.0},
            {'student_id': 'ST008', 'first_name': 'Kavita', 'last_name': 'Nair', 'email': 'kavita.nair@eduguard.edu', 'department': 'Chemistry', 'gpa': 8.5, 'attendance_percentage': 90.0},
        ]
        
        for student_data in students_data:
            student = Student(**student_data)
            db.session.add(student)
        
        db.session.commit()
        
        # Create attendance records
        for student in Student.query.all():
            for i in range(10):
                attendance_date = date.today() - timedelta(days=i)
                status = 'present' if i % 3 != 0 else 'absent'
                attendance = Attendance(
                    student_id=student.id,
                    date=attendance_date,
                    status=status,
                    subject='Math'
                )
                db.session.add(attendance)
        
        db.session.commit()
        
        # Create risk profiles (CGPA out of 10 scale)
        for student in Student.query.all():
            risk_level = 'low'
            gpa_risk = False
            attendance_risk = False
            
            # CGPA thresholds: < 6.0 = high risk, < 7.0 = medium risk
            if student.gpa < 6.0:
                risk_level = 'high'
                gpa_risk = True
            elif student.gpa < 7.0:
                risk_level = 'medium'
            
            if student.attendance_percentage < 70:
                risk_level = 'high'
                attendance_risk = True
            elif student.attendance_percentage < 80:
                risk_level = 'medium'
            
            risk = RiskProfile(
                student_id=student.id,
                risk_level=risk_level,
                gpa_risk=gpa_risk,
                attendance_risk=attendance_risk
            )
            db.session.add(risk)
        
        db.session.commit()
        print("✅ Sample data created successfully!")

if __name__ == '__main__':
    with app.app_context():
        create_sample_data()
    
    print("🚀 EduGuard Application Starting...")
    print("🌐 Access at: http://127.0.0.1:5000")
    print("🔐 LOGIN CREDENTIALS:")
    print("==================================================")
    print("ADMIN: admin@eduguard.edu / admin123")
    print("FACULTY: faculty@eduguard.edu / faculty123")
    print("==================================================")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
