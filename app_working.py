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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    gpa = db.Column(db.Float, nullable=False)
    attendance_percentage = db.Column(db.Float, nullable=False)
    
    # Enhanced Risk Factors
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    socioeconomic_status = db.Column(db.String(20))  # Low, Medium, High
    first_generation = db.Column(db.Boolean, default=False)  # First generation college student
    employment_status = db.Column(db.String(20))  # Unemployed, Part-time, Full-time
    work_hours_per_week = db.Column(db.Integer)
    family_support = db.Column(db.Integer, default=5)  # 1-10 scale
    peer_relationships = db.Column(db.Integer, default=5)  # 1-10 scale
    mental_health_score = db.Column(db.Integer, default=5)  # 1-10 scale (higher = better)
    physical_health_score = db.Column(db.Integer, default=5)  # 1-10 scale (higher = better)
    financial_stress = db.Column(db.Integer, default=5)  # 1-10 scale (higher = more stress)
    academic_motivation = db.Column(db.Integer, default=5)  # 1-10 scale (higher = better)
    study_hours_per_week = db.Column(db.Integer, default=20)
    extracurricular_participation = db.Column(db.Boolean, default=False)
    living_situation = db.Column(db.String(20))  # With family, alone, dorm, etc.
    commute_time = db.Column(db.Integer)  # Minutes per day
    previous_dropout = db.Column(db.Boolean, default=False)
    learning_disability = db.Column(db.Boolean, default=False)
    language_barrier = db.Column(db.Boolean, default=False)
    internet_access = db.Column(db.Boolean, default=True)
    device_access = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # COMPREHENSIVE 360° STUDENT PROFILE FACTORS
    
    # 1. FINANCIAL CONDITION FACTORS
    family_income_level = db.Column(db.String(20))  # Low/Medium/High
    scholarship_eligibility = db.Column(db.Boolean, default=False)
    fee_payment_delays = db.Column(db.Integer, default=0)  # Number of delayed payments
    part_time_job_dependency = db.Column(db.Boolean, default=False)
    financial_aid_received = db.Column(db.Boolean, default=False)
    loan_status = db.Column(db.String(20))  # None/Requested/Approved/Rejected
    
    # 2. ACADEMIC PERFORMANCE FACTORS
    grades_trend = db.Column(db.String(20))  # Improving/Stable/Declining
    backlog_subjects = db.Column(db.Integer, default=0)
    remedial_classes_participation = db.Column(db.Boolean, default=False)
    assignment_completion_rate = db.Column(db.Float, default=100.0)
    project_submission_status = db.Column(db.String(20))  # On Time/Late/Missing
    
    # 3. PSYCHOLOGICAL & EMOTIONAL FACTORS
    stress_anxiety_level = db.Column(db.Integer, default=5)  # 1-10 scale
    motivation_score = db.Column(db.Integer, default=7)  # 1-10 scale
    peer_relationship_quality = db.Column(db.String(20))  # Good/Average/Poor
    bullying_incidents = db.Column(db.Integer, default=0)
    counseling_sessions_attended = db.Column(db.Integer, default=0)
    self_confidence_level = db.Column(db.Integer, default=7)  # 1-10 scale
    
    # 4. FAMILY & SOCIAL BACKGROUND FACTORS
    parent_involvement_level = db.Column(db.String(20))  # High/Medium/Low
    family_conflicts_status = db.Column(db.String(20))  # None/Moderate/Severe
    caregiving_responsibilities = db.Column(db.Boolean, default=False)
    family_earning_responsibility = db.Column(db.Boolean, default=False)
    relocation_history = db.Column(db.Integer, default=0)  # Number of relocations
    family_education_background = db.Column(db.String(50))  # Parent's education level
    
    # 5. HEALTH & WELL-BEING FACTORS
    chronic_illness_status = db.Column(db.String(20))  # None/Mild/Severe
    disability_status = db.Column(db.String(20))  # None/Physical/Mental/Learning
    medical_checkup_frequency = db.Column(db.Integer, default=0)  # Per year
    sleep_quality_score = db.Column(db.Integer, default=7)  # 1-10 scale
    nutrition_habits_score = db.Column(db.Integer, default=7)  # 1-10 scale
    healthcare_access = db.Column(db.Boolean, default=True)
    mental_health_status = db.Column(db.String(20))  # Good/Fair/Poor
    
    # 6. INSTITUTIONAL FACTORS
    teacher_student_relationship = db.Column(db.Integer, default=7)  # 1-10 scale
    mentorship_availability = db.Column(db.Boolean, default=False)
    curriculum_flexibility = db.Column(db.String(20))  # High/Medium/Low
    student_satisfaction_score = db.Column(db.Integer, default=7)  # 1-10 scale
    teacher_feedback_quality = db.Column(db.String(20))  # Good/Average/Poor
    institutional_support = db.Column(db.String(20))  # High/Medium/Low
    
    # 7. EXTRACURRICULAR & ENGAGEMENT FACTORS
    clubs_participation = db.Column(db.Boolean, default=False)
    sports_participation = db.Column(db.Boolean, default=False)
    events_participation = db.Column(db.Integer, default=0)  # Number of events
    leadership_roles = db.Column(db.Boolean, default=False)
    volunteer_hours = db.Column(db.Integer, default=0)  # Hours per month
    peer_group_involvement = db.Column(db.String(20))  # High/Medium/Low
    
    # 8. TECHNOLOGY & ACCESSIBILITY FACTORS
    laptop_access = db.Column(db.Boolean, default=True)
    smartphone_access = db.Column(db.Boolean, default=True)
    internet_quality = db.Column(db.String(20))  # Good/Average/Poor
    online_class_attendance_rate = db.Column(db.Float, default=100.0)
    digital_literacy_score = db.Column(db.Integer, default=7)  # 1-10 scale
    device_loan_status = db.Column(db.String(20))  # None/Requested/Approved
    
    # CRITICAL REAL-WORLD DROPOUT FACTORS
    stress_level = db.Column(db.Integer, default=5)  # 1-10 scale (higher = more stress)
    financial_difficulty = db.Column(db.Integer, default=5)  # 1-10 scale (higher = more difficulty)
    academic_interest = db.Column(db.Integer, default=5)  # 1-10 scale (higher = more interested)
    social_integration = db.Column(db.Integer, default=5)  # 1-10 scale (higher = better integrated)
    personal_problems = db.Column(db.Text)  # Family issues, relationship problems, etc.
    health_issues = db.Column(db.Text)  # Chronic illness, disabilities, accidents
    trauma_history = db.Column(db.Boolean, default=False)  # Recent trauma, abuse, etc.
    substance_abuse = db.Column(db.Boolean, default=False)  # Drug/alcohol abuse
    legal_troubles = db.Column(db.Boolean, default=False)  # Legal issues, court cases
    housing_instability = db.Column(db.Boolean, default=False)  # Homelessness, frequent moves
    food_insecurity = db.Column(db.Boolean, default=False)  # Hunger, lack of nutrition
    transportation_issues = db.Column(db.Boolean, default=False)  # No reliable transport
    pregnancy_parenting = db.Column(db.Boolean, default=False)  # Pregnancy or parenting responsibilities
    bereavement_grief = db.Column(db.Boolean, default=False)  # Death of family member
    academic_struggles = db.Column(db.Text)  # Learning disabilities, course difficulty
    time_management_issues = db.Column(db.Boolean, default=False)  # Can't manage time effectively
    sleep_deprivation = db.Column(db.Integer, default=7)  # Hours of sleep per night (1-10 scale, lower = worse)
    nutrition_status = db.Column(db.Integer, default=5)  # 1-10 scale (higher = better nutrition)
    social_media_addiction = db.Column(db.Boolean, default=False)  # Excessive social media use
    bullying_harassment = db.Column(db.Boolean, default=False)  # Being bullied or harassed
    isolation_loneliness = db.Column(db.Integer, default=5)  # 1-10 scale (higher = more isolated)
    career_uncertainty = db.Column(db.Integer, default=5)  # 1-10 scale (higher = more uncertain)
    future_anxiety = db.Column(db.Integer, default=5)  # 1-10 scale (higher = more anxious)
    
    # Support Resources Access
    counseling_access = db.Column(db.Boolean, default=False)
    tutoring_available = db.Column(db.Boolean, default=False)
    mentorship_program = db.Column(db.Boolean, default=False)
    financial_aid_available = db.Column(db.Boolean, default=False)
    mental_health_services = db.Column(db.Boolean, default=False)
    academic_support_services = db.Column(db.Boolean, default=False)
    crisis_intervention = db.Column(db.Boolean, default=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='students')
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    risk_profile = db.relationship('RiskProfile', backref='student', uselist=False)

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
    risk_factors = db.Column(db.Text)
    risk_score = db.Column(db.Float, nullable=False)  # 0-100 comprehensive score
    
    # Academic Risk Factors
    gpa_risk = db.Column(db.Boolean, default=False)
    attendance_risk = db.Column(db.Boolean, default=False)
    
    # Critical Real-World Risk Factors
    stress_risk = db.Column(db.Boolean, default=False)
    financial_risk = db.Column(db.Boolean, default=False)
    mental_health_risk = db.Column(db.Boolean, default=False)
    trauma_risk = db.Column(db.Boolean, default=False)
    substance_abuse_risk = db.Column(db.Boolean, default=False)
    legal_risk = db.Column(db.Boolean, default=False)
    housing_risk = db.Column(db.Boolean, default=False)
    food_risk = db.Column(db.Boolean, default=False)
    caregiving_risk = db.Column(db.Boolean, default=False)
    bereavement_risk = db.Column(db.Boolean, default=False)
    bullying_risk = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
        
        # Create sample students with comprehensive real-world risk factors
        students_data = [
            {
                'student_id': 'ST001', 
                'first_name': 'Rahul', 
                'last_name': 'Sharma', 
                'email': 'rahul.sharma@eduguard.edu', 
                'department': 'Computer Science', 
                'gpa': 8.2, 
                'attendance_percentage': 85.0,
                'age': 20,
                'gender': 'Male',
                'socioeconomic_status': 'Medium',
                'first_generation': False,
                'employment_status': 'Part-time',
                'work_hours_per_week': 15,
                'family_support': 8,
                'peer_relationships': 7,
                'mental_health_score': 7,
                'physical_health_score': 8,
                'financial_stress': 4,
                'academic_motivation': 8,
                'study_hours_per_week': 25,
                'extracurricular_participation': True,
                'living_situation': 'Dorm',
                'commute_time': 30,
                'previous_dropout': False,
                'learning_disability': False,
                'language_barrier': False,
                'internet_access': True,
                'device_access': True,
                # CRITICAL REAL-WORLD FACTORS
                'stress_level': 3,  # Low stress
                'financial_difficulty': 4,  # Low difficulty
                'academic_interest': 9,  # High interest
                'social_integration': 8,  # Good integration
                'personal_problems': 'None',
                'health_issues': 'None',
                'trauma_history': False,
                'substance_abuse': False,
                'legal_troubles': False,
                'housing_instability': False,
                'food_insecurity': False,
                'transportation_issues': False,
                'caregiving_responsibilities': False,
                'pregnancy_parenting': False,
                'bereavement_grief': False,
                'academic_struggles': 'None',
                'time_management_issues': False,
                'sleep_deprivation': 7,
                'nutrition_status': 8,
                'social_media_addiction': False,
                'bullying_harassment': False,
                'isolation_loneliness': 3,  # Some loneliness
                'career_uncertainty': 2,  # Clear career goals
                'future_anxiety': 3,  # Some anxiety about future
                'counseling_access': True,
                'tutoring_available': True,
                'mentorship_program': True,
                'financial_aid_available': False,
                'mental_health_services': True,
                'academic_support_services': True,
                'crisis_intervention': False
            },
            {
                'student_id': 'ST002', 
                'first_name': 'Priya', 
                'last_name': 'Patel', 
                'email': 'priya.patel@eduguard.edu', 
                'department': 'Engineering', 
                'gpa': 7.5, 
                'attendance_percentage': 75.0,
                'age': 21,
                'gender': 'Female',
                'socioeconomic_status': 'Low',
                'first_generation': True,
                'employment_status': 'Full-time',
                'work_hours_per_week': 40,
                'family_support': 4,
                'peer_relationships': 5,
                'mental_health_score': 4,
                'physical_health_score': 6,
                'financial_stress': 8,
                'academic_motivation': 6,
                'study_hours_per_week': 15,
                'extracurricular_participation': False,
                'living_situation': 'With Family',
                'commute_time': 60,
                'previous_dropout': False,
                'learning_disability': False,
                'language_barrier': False,
                'internet_access': True,
                'device_access': True,
                # CRITICAL REAL-WORLD FACTORS
                'stress_level': 8,  # High stress
                'financial_difficulty': 9,  # High difficulty
                'academic_interest': 3,  # Low interest
                'social_integration': 4,  # Poor integration
                'personal_problems': 'Family financial issues, parental pressure',
                'health_issues': 'Chronic migraines',
                'trauma_history': False,
                'substance_abuse': False,
                'legal_troubles': False,
                'housing_instability': False,
                'food_insecurity': True,
                'transportation_issues': False,
                'caregiving_responsibilities': True,  # Caring for sick parent
                'pregnancy_parenting': False,
                'bereavement_grief': False,
                'academic_struggles': 'Math anxiety, test anxiety',
                'time_management_issues': True,
                'sleep_deprivation': 5,  # Poor sleep
                'nutrition_status': 3,  # Poor nutrition
                'social_media_addiction': False,
                'bullying_harassment': False,
                'isolation_loneliness': 7,  # High isolation
                'career_uncertainty': 8,  # High uncertainty
                'future_anxiety': 7,  # High anxiety
                'counseling_access': False,
                'tutoring_available': False,
                'mentorship_program': False,
                'financial_aid_available': False,
                'mental_health_services': False,
                'academic_support_services': False,
                'crisis_intervention': False
            },
            {
                'student_id': 'ST003', 
                'first_name': 'Amit', 
                'last_name': 'Kumar', 
                'email': 'amit.kumar@eduguard.edu', 
                'department': 'Business', 
                'gpa': 8.8, 
                'attendance_percentage': 92.0,
                'age': 19,
                'gender': 'Male',
                'socioeconomic_status': 'High',
                'first_generation': False,
                'employment_status': 'Unemployed',
                'work_hours_per_week': 0,
                'family_support': 9,
                'peer_relationships': 8,
                'mental_health_score': 9,
                'physical_health_score': 8,
                'financial_stress': 2,
                'academic_motivation': 9,
                'study_hours_per_week': 30,
                'extracurricular_participation': True,
                'living_situation': 'Dorm',
                'commute_time': 15,
                'previous_dropout': False,
                'learning_disability': False,
                'language_barrier': False,
                'internet_access': True,
                'device_access': True,
                # CRITICAL REAL-WORLD FACTORS
                'stress_level': 2,  # Low stress
                'financial_difficulty': 1,  # Low difficulty
                'academic_interest': 10,  # High interest
                'social_integration': 9,  # Excellent integration
                'personal_problems': 'None',
                'health_issues': 'None',
                'trauma_history': False,
                'substance_abuse': False,
                'legal_troubles': False,
                'housing_instability': False,
                'food_insecurity': False,
                'transportation_issues': False,
                'caregiving_responsibilities': False,
                'pregnancy_parenting': False,
                'bereavement_grief': False,
                'academic_struggles': 'None',
                'time_management_issues': False,
                'sleep_deprivation': 9,  # Good sleep
                'nutrition_status': 9,  # Good nutrition
                'social_media_addiction': False,
                'bullying_harassment': False,
                'isolation_loneliness': 2,  # Some loneliness
                'career_uncertainty': 1,  # Clear career goals
                'future_anxiety': 2,  # Low anxiety
                'counseling_access': True,
                'tutoring_available': True,
                'mentorship_program': True,
                'financial_aid_available': True,
                'mental_health_services': True,
                'academic_support_services': True,
                'crisis_intervention': False
            },
            {
                'student_id': 'ST004', 
                'first_name': 'Sneha', 
                'last_name': 'Reddy', 
                'email': 'sneha.reddy@eduguard.edu', 
                'department': 'Computer Science', 
                'gpa': 6.2, 
                'attendance_percentage': 65.0,
                'age': 22,
                'gender': 'Female',
                'socioeconomic_status': 'Low',
                'first_generation': True,
                'employment_status': 'Full-time',
                'work_hours_per_week': 35,
                'family_support': 3,
                'peer_relationships': 4,
                'mental_health_score': 3,
                'physical_health_score': 4,
                'financial_stress': 9,
                'academic_motivation': 3,
                'study_hours_per_week': 10,
                'extracurricular_participation': False,
                'living_situation': 'Alone',
                'commute_time': 90,
                'previous_dropout': True,
                'learning_disability': True,
                'language_barrier': False,
                'internet_access': False,
                'device_access': True,
                # CRITICAL REAL-WORLD FACTORS
                'stress_level': 9,  # Very high stress
                'financial_difficulty': 10,  # Extreme difficulty
                'academic_interest': 2,  # Very low interest
                'social_integration': 2,  # Poor integration
                'personal_problems': 'Family financial crisis, depression',
                'health_issues': 'Chronic illness, recent accident',
                'trauma_history': True,
                'substance_abuse': False,
                'legal_troubles': False,
                'housing_instability': True,  # Frequent moves
                'food_insecurity': True,
                'transportation_issues': True,
                'caregiving_responsibilities': False,
                'pregnancy_parenting': False,
                'bereavement_grief': False,
                'academic_struggles': 'Severe learning disability',
                'time_management_issues': True,
                'sleep_deprivation': 3,  # Very poor sleep
                'nutrition_status': 2,  # Poor nutrition
                'social_media_addiction': False,
                'bullying_harassment': True,
                'isolation_loneliness': 8,  # High isolation
                'career_uncertainty': 9,  # High uncertainty
                'future_anxiety': 9,  # High anxiety
                'counseling_access': False,
                'tutoring_available': False,
                'mentorship_program': False,
                'financial_aid_available': False,
                'mental_health_services': False,
                'academic_support_services': False,
                'crisis_intervention': True
            },
            {
                'student_id': 'ST005', 
                'first_name': 'Vikram', 
                'last_name': 'Singh', 
                'email': 'vikram.singh@eduguard.edu', 
                'department': 'Engineering', 
                'gpa': 9.1, 
                'attendance_percentage': 95.0,
                'age': 20,
                'gender': 'Male',
                'socioeconomic_status': 'Medium',
                'first_generation': False,
                'employment_status': 'Part-time',
                'work_hours_per_week': 12,
                'family_support': 8,
                'peer_relationships': 9,
                'mental_health_score': 8,
                'physical_health_score': 9,
                'financial_stress': 3,
                'academic_motivation': 9,
                'study_hours_per_week': 35,
                'extracurricular_participation': True,
                'living_situation': 'Dorm',
                'commute_time': 20,
                'previous_dropout': False,
                'learning_disability': False,
                'language_barrier': False,
                'internet_access': True,
                'device_access': True,
                # CRITICAL REAL-WORLD FACTORS
                'stress_level': 2,  # Low stress
                'financial_difficulty': 3,  # Low difficulty
                'academic_interest': 10,  # High interest
                'social_integration': 9,  # Excellent integration
                'personal_problems': 'None',
                'health_issues': 'None',
                'trauma_history': False,
                'substance_abuse': False,
                'legal_troubles': False,
                'housing_instability': False,
                'food_insecurity': False,
                'transportation_issues': False,
                'caregiving_responsibilities': False,
                'pregnancy_parenting': False,
                'bereavement_grief': False,
                'academic_struggles': 'None',
                'time_management_issues': False,
                'sleep_deprivation': 8,  # Good sleep
                'nutrition_status': 9,  # Good nutrition
                'social_media_addiction': False,
                'bullying_harassment': False,
                'isolation_loneliness': 1,  # Some isolation
                'career_uncertainty': 1,  # Clear career goals
                'future_anxiety': 2,  # Low anxiety
                'counseling_access': True,
                'tutoring_available': True,
                'mentorship_program': True,
                'financial_aid_available': True,
                'mental_health_services': True,
                'academic_support_services': True,
                'crisis_intervention': False
            },
            {
                'student_id': 'ST006', 
                'first_name': 'Anjali', 
                'last_name': 'Gupta', 
                'email': 'anjali.gupta@eduguard.edu', 
                'department': 'Mathematics', 
                'gpa': 7.8, 
                'attendance_percentage': 88.0,
                'age': 21,
                'gender': 'Female',
                'socioeconomic_status': 'Medium',
                'first_generation': False,
                'employment_status': 'Unemployed',
                'work_hours_per_week': 0,
                'family_support': 7,
                'peer_relationships': 8,
                'mental_health_score': 6,
                'physical_health_score': 7,
                'financial_stress': 5,
                'academic_motivation': 8,
                'study_hours_per_week': 28,
                'extracurricular_participation': True,
                'living_situation': 'With Family',
                'commute_time': 45,
                'previous_dropout': False,
                'learning_disability': False,
                'language_barrier': True,
                'internet_access': True,
                'device_access': True,
                # CRITICAL REAL-WORLD FACTORS
                'stress_level': 4,  # Moderate stress
                'financial_difficulty': 6,  # Moderate difficulty
                'academic_interest': 7,  # Good interest
                'social_integration': 8,  # Good integration
                'personal_problems': 'None',
                'health_issues': 'None',
                'trauma_history': False,
                'substance_abuse': False,
                'legal_troubles': False,
                'housing_instability': False,
                'food_insecurity': False,
                'transportation_issues': False,
                'caregiving_responsibilities': False,
                'pregnancy_parenting': False,
                'bereavement_grief': False,
                'academic_struggles': 'None',
                'time_management_issues': False,
                'sleep_deprivation': 6,  # Poor sleep
                'nutrition_status': 6,  # Moderate nutrition
                'social_media_addiction': False,
                'bullying_harassment': False,
                'isolation_loneliness': 4,  # Some isolation
                'career_uncertainty': 6,  # Moderate uncertainty
                'future_anxiety': 5,  # Moderate anxiety
                'counseling_access': True,
                'tutoring_available': True,
                'mentorship_program': True,
                'financial_aid_available': True,
                'mental_health_services': True,
                'academic_support_services': True,
                'crisis_intervention': False
            },
            {
                'student_id': 'ST007', 
                'first_name': 'Rohit', 
                'last_name': 'Verma', 
                'email': 'rohit.verma@eduguard.edu', 
                'department': 'Physics', 
                'gpa': 6.9, 
                'attendance_percentage': 70.0,
                'age': 23,
                'gender': 'Male',
                'socioeconomic_status': 'Low',
                'first_generation': True,
                'employment_status': 'Full-time',
                'work_hours_per_week': 45,
                'family_support': 2,
                'peer_relationships': 3,
                'mental_health_score': 4,
                'physical_health_score': 5,
                'financial_stress': 8,
                'academic_motivation': 4,
                'study_hours_per_week': 12,
                'extracurricular_participation': False,
                'living_situation': 'Alone',
                'commute_time': 75,
                'previous_dropout': False,
                'learning_disability': False,
                'language_barrier': False,
                'internet_access': True,
                'device_access': False,
                # CRITICAL REAL-WORLD FACTORS
                'stress_level': 8,  # High stress
                'financial_difficulty': 9,  # High difficulty
                'academic_interest': 3,  # Low interest
                'social_integration': 3,  # Poor integration
                'personal_problems': 'Family conflicts, financial pressure',
                'health_issues': 'Back injury, medical issues',
                'trauma_history': False,
                'substance_abuse': False,
                'legal_troubles': False,
                'housing_instability': True,  # Frequent moves
                'food_insecurity': True,
                'transportation_issues': True,
                'caregiving_responsibilities': False,
                'pregnancy_parenting': False,
                'bereavement_grief': False,
                'academic_struggles': 'Attention deficit disorder',
                'time_management_issues': True,
                'sleep_deprivation': 4,  # Poor sleep
                'nutrition_status': 4,  # Poor nutrition
                'social_media_addiction': False,
                'bullying_harassment': False,
                'isolation_loneliness': 9,  # High isolation
                'career_uncertainty': 8,  # High uncertainty
                'future_anxiety': 8,  # High anxiety
                'counseling_access': False,
                'tutoring_available': False,
                'mentorship_program': False,
                'financial_aid_available': False,
                'mental_health_services': False,
                'academic_support_services': False,
                'crisis_intervention': True
            },
            {
                'student_id': 'ST008', 
                'first_name': 'Kavita', 
                'last_name': 'Nair', 
                'email': 'kavita.nair@eduguard.edu', 
                'department': 'Chemistry', 
                'gpa': 8.5, 
                'attendance_percentage': 90.0,
                'age': 20,
                'gender': 'Female',
                'socioeconomic_status': 'High',
                'first_generation': False,
                'employment_status': 'Part-time',
                'work_hours_per_week': 10,
                'family_support': 9,
                'peer_relationships': 8,
                'mental_health_score': 8,
                'physical_health_score': 9,
                'financial_stress': 2,
                'academic_motivation': 9,
                'study_hours_per_week': 32,
                'extracurricular_participation': True,
                'living_situation': 'Dorm',
                'commute_time': 25,
                'previous_dropout': False,
                'learning_disability': False,
                'language_barrier': False,
                'internet_access': True,
                'device_access': True,
                # CRITICAL REAL-WORLD FACTORS
                'stress_level': 1,  # Low stress
                'financial_difficulty': 2,  # Low difficulty
                'academic_interest': 10,  # High interest
                'social_integration': 9,  # Excellent integration
                'personal_problems': 'None',
                'health_issues': 'None',
                'trauma_history': False,
                'substance_abuse': False,
                'legal_troubles': False,
                'housing_instability': False,
                'food_insecurity': False,
                'transportation_issues': False,
                'caregiving_responsibilities': False,
                'pregnancy_parenting': False,
                'bereavement_grief': False,
                'academic_struggles': 'None',
                'time_management_issues': False,
                'sleep_deprivation': 9,  # Good sleep
                'nutrition_status': 9,  # Good nutrition
                'social_media_addiction': False,
                'bullying_harassment': False,
                'isolation_loneliness': 1,  # Some loneliness
                'career_uncertainty': 1,  # Clear career goals
                'future_anxiety': 2,  # Low anxiety
                'counseling_access': True,
                'tutoring_available': True,
                'mentorship_program': True,
                'financial_aid_available': True,
                'mental_health_services': True,
                'academic_support_services': True,
                'crisis_intervention': False
            }
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
        
        # Create comprehensive risk profiles (real-world factors)
        for student in Student.query.all():
            risk_level = 'low'
            risk_factors = []
            
            # Academic Risk Factors (20% weight)
            if student.gpa < 6.0:
                risk_level = 'high'
                risk_factors.append('Low CGPA')
            elif student.gpa < 7.0:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Below Average CGPA')
            
            if student.attendance_percentage < 70:
                risk_level = 'high'
                risk_factors.append('Poor Attendance')
            elif student.attendance_percentage < 80:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Low Attendance')
            
            # CRITICAL REAL-WORLD DROPOUT FACTORS (80% weight)
            
            # Stress Factors (15% weight)
            if student.stress_level >= 8:
                risk_level = 'high'
                risk_factors.append('Severe Stress')
            elif student.stress_level >= 6:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('High Stress')
            
            # Financial Factors (15% weight)
            if student.financial_difficulty >= 9:
                risk_level = 'high'
                risk_factors.append('Extreme Financial Difficulty')
            elif student.financial_difficulty >= 7:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('High Financial Difficulty')
            
            # Academic Interest (10% weight)
            if student.academic_interest <= 2:
                risk_level = 'high'
                risk_factors.append('No Academic Interest')
            elif student.academic_interest <= 4:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Low Academic Interest')
            
            # Social Integration (10% weight)
            if student.social_integration <= 3:
                risk_level = 'high'
                risk_factors.append('Poor Social Integration')
            elif student.social_integration <= 5:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Limited Social Integration')
            
            # Mental Health (10% weight)
            if student.mental_health_score <= 3:
                risk_level = 'high'
                risk_factors.append('Mental Health Crisis')
            elif student.mental_health_score <= 5:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Mental Health Issues')
            
            # Personal Problems (10% weight)
            if student.personal_problems and student.personal_problems != 'None':
                if 'family' in student.personal_problems.lower() or 'financial' in student.personal_problems.lower():
                    risk_level = 'high'
                    risk_factors.append('Family/Financial Problems')
                else:
                    if risk_level != 'high':
                        risk_level = 'medium'
                    risk_factors.append('Personal Problems')
            
            # Health Issues (10% weight)
            if student.health_issues and student.health_issues != 'None':
                if 'chronic' in student.health_issues.lower() or 'severe' in student.health_issues.lower():
                    risk_level = 'high'
                    risk_factors.append('Severe Health Issues')
                else:
                    if risk_level != 'high':
                        risk_level = 'medium'
                    risk_factors.append('Health Problems')
            
            # Trauma History (15% weight)
            if student.trauma_history:
                risk_level = 'high'
                risk_factors.append('Trauma History')
            
            # Substance Abuse (15% weight)
            if student.substance_abuse:
                risk_level = 'high'
                risk_factors.append('Substance Abuse')
            
            # Legal Troubles (15% weight)
            if student.legal_troubles:
                risk_level = 'high'
                risk_factors.append('Legal Issues')
            
            # Housing Instability (10% weight)
            if student.housing_instability:
                risk_level = 'high'
                risk_factors.append('Housing Instability')
            
            # Food Insecurity (10% weight)
            if student.food_insecurity:
                risk_level = 'high'
                risk_factors.append('Food Insecurity')
            
            # Transportation Issues (5% weight)
            if student.transportation_issues:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Transportation Issues')
            
            # Caregiving Responsibilities (10% weight)
            if student.caregiving_responsibilities:
                risk_level = 'high'
                risk_factors.append('Caregiving Responsibilities')
            
            # Pregnancy/Parenting (15% weight)
            if student.pregnancy_parenting:
                risk_level = 'high'
                risk_factors.append('Pregnancy/Parenting')
            
            # Bereavement/Grief (15% weight)
            if student.bereavement_grief:
                risk_level = 'high'
                risk_factors.append('Bereavement/Grief')
            
            # Time Management Issues (5% weight)
            if student.time_management_issues:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Time Management Issues')
            
            # Sleep Deprivation (5% weight)
            if student.sleep_deprivation <= 3:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Severe Sleep Deprivation')
            
            # Bullying/Harassment (15% weight)
            if student.bullying_harassment:
                risk_level = 'high'
                risk_factors.append('Bullying/Harassment')
            
            # Isolation/Loneliness (10% weight)
            if student.isolation_loneliness >= 8:
                risk_level = 'high'
                risk_factors.append('Severe Isolation')
            elif student.isolation_loneliness >= 6:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('High Isolation')
            
            # Career Uncertainty (5% weight)
            if student.career_uncertainty >= 8:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Career Uncertainty')
            
            # Future Anxiety (5% weight)
            if student.future_anxiety >= 8:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('Future Anxiety')
            
            # Support Resources Access (Negative factors if NO access)
            if not student.counseling_access:
                if risk_level != 'high':
                    risk_level = 'medium'
                risk_factors.append('No Counseling Access')
            
            if not student.mental_health_services and student.mental_health_score <= 5:
                risk_level = 'high'
                risk_factors.append('No Mental Health Services')
            
            if not student.financial_aid_available and student.financial_difficulty >= 7:
                risk_level = 'high'
                risk_factors.append('No Financial Aid Available')
            
            # Calculate comprehensive risk score (0-100)
            risk_score = 0
            
            # Academic factors (20% weight)
            gpa_risk = max(0, (7.0 - student.gpa) / 7.0) * 10
            attendance_risk = max(0, (80 - student.attendance_percentage) / 80) * 10
            risk_score += gpa_risk + attendance_risk
            
            # Critical real-world factors (80% weight)
            stress_risk = max(0, (student.stress_level - 5) / 5) * 15
            financial_risk = max(0, (student.financial_difficulty - 5) / 5) * 15
            interest_risk = max(0, (5 - student.academic_interest) / 5) * 10
            social_risk = max(0, (5 - student.social_integration) / 5) * 10
            mental_risk = max(0, (5 - student.mental_health_score) / 5) * 10
            
            risk_score += stress_risk + financial_risk + interest_risk + social_risk + mental_risk
            
            # High-impact factors (15 points each)
            if student.trauma_history:
                risk_score += 15
            if student.substance_abuse:
                risk_score += 15
            if student.legal_troubles:
                risk_score += 15
            if student.housing_instability:
                risk_score += 10
            if student.food_insecurity:
                risk_score += 10
            if student.caregiving_responsibilities:
                risk_score += 10
            if student.pregnancy_parenting:
                risk_score += 15
            if student.bereavement_grief:
                risk_score += 15
            if student.bullying_harassment:
                risk_score += 15
            
            # Medium-impact factors (5-10 points each)
            if student.personal_problems and student.personal_problems != 'None':
                risk_score += 8
            if student.health_issues and student.health_issues != 'None':
                risk_score += 8
            if student.time_management_issues:
                risk_score += 5
            if student.sleep_deprivation <= 3:
                risk_score += 5
            if student.isolation_loneliness >= 8:
                risk_score += 10
            if student.transportation_issues:
                risk_score += 5
            if not student.counseling_access:
                risk_score += 5
            if not student.mental_health_services and student.mental_health_score <= 5:
                risk_score += 10
            if not student.financial_aid_available and student.financial_difficulty >= 7:
                risk_score += 10
            
            # Cap risk score at 100
            risk_score = min(100, risk_score)
            
            risk = RiskProfile(
                student_id=student.id,
                risk_level=risk_level,
                risk_factors=', '.join(risk_factors) if risk_factors else 'None',
                risk_score=risk_score,
                gpa_risk=gpa_risk > 0,
                attendance_risk=attendance_risk > 0,
                mental_health_risk=mental_risk > 0,
                financial_risk=financial_risk > 0,
                stress_risk=stress_risk > 0,
                trauma_risk=student.trauma_history,
                substance_abuse_risk=student.substance_abuse,
                legal_risk=student.legal_troubles,
                housing_risk=student.housing_instability,
                food_risk=student.food_insecurity,
                caregiving_risk=student.caregiving_responsibilities,
                bereavement_risk=student.bereavement_grief,
                bullying_risk=student.bullying_harassment
            )
            db.session.add(risk)
        
        db.session.commit()
        print("✅ Sample data created successfully!")

# Import AI routes
from ai_routes import ai_bp

# Register AI blueprint
app.register_blueprint(ai_bp)

if __name__ == '__main__':
    with app.app_context():
        create_sample_data()
    
    print("🚀 Student Dropout Prevention System Starting...")
    print("🌐 Access at: http://127.0.0.1:5000")
    print("🔐 LOGIN CREDENTIALS:")
    print("==================================================")
    print("ADMIN: admin@eduguard.edu / admin123")
    print("FACULTY: faculty@eduguard.edu / faculty123")
    print("==================================================")
    app.run(debug=True, host='0.0.0.0', port=5000)
