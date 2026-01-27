from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student, Attendance, AcademicRecord, Intervention, RiskProfile
from utils import update_student_risk
from datetime import datetime

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

# --- Authentication Routes ---
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        # Simple check (In production, use werkzeug.security.check_password_hash)
        # For this demo, assuming seeded users have raw passwords or handle hash in seed
        # We will assume check_password_hash is used if password_hash is set
        if not user or user.password_hash != password: 
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        return redirect(url_for('main.dashboard'))
        
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# --- Main Routes ---
@main.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
@login_required
def dashboard():
    # KPI Calculations
    total_students = Student.query.count()
    
    # Calculate risks for all students to ensure fresh data
    # In real app, this would be a background job.
    # students = Student.query.all()
    # for s in students:
    #     update_student_risk(s)
        
    high_risk_count = RiskProfile.query.filter_by(risk_level='High').count()
    medium_risk_count = RiskProfile.query.filter_by(risk_level='Medium').count()
    
    # Recent interventions
    recent_interventions = Intervention.query.order_by(Intervention.date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           total_students=total_students,
                           high_risk_count=high_risk_count,
                           medium_risk_count=medium_risk_count,
                           recent_interventions=recent_interventions)

@main.route('/students')
@login_required
def students():
    risk_filter = request.args.get('risk')
    search_query = request.args.get('search')
    
    query = Student.query.join(RiskProfile)
    
    if risk_filter:
        query = query.filter(RiskProfile.risk_level == risk_filter)
        
    if search_query:
        query = query.filter(
            (Student.first_name.ilike(f'%{search_query}%')) | 
            (Student.last_name.ilike(f'%{search_query}%')) |
            (Student.student_id.ilike(f'%{search_query}%'))
        )
        
    students_list = query.all()
    return render_template('students.html', students=students_list)

@main.route('/student/<int:id>')
@login_required
def student_detail(id):
    student = Student.query.get_or_404(id)
    risk_profile = update_student_risk(student) # Ensure latest risk is shown
    
    attendance_records = Attendance.query.filter_by(student_id=id).order_by(Attendance.date.desc()).limit(10).all()
    academic_records = AcademicRecord.query.filter_by(student_id=id).order_by(AcademicRecord.date.desc()).all()
    interventions = Intervention.query.filter_by(student_id=id).order_by(Intervention.date.desc()).all()
    
    return render_template('student_detail.html', 
                           student=student, 
                           risk=risk_profile,
                           attendance=attendance_records,
                           grades=academic_records,
                           interventions=interventions)

@main.route('/student/<int:id>/add_intervention', methods=['POST'])
@login_required
def add_intervention(id):
    type = request.form.get('type')
    notes = request.form.get('notes')
    
    intervention = Intervention(
        student_id=id,
        type=type,
        notes=notes,
        date=datetime.utcnow()
    )
    db.session.add(intervention)
    db.session.commit()
    flash('Intervention recorded successfully.', 'success')
    return redirect(url_for('main.student_detail', id=id))

@main.route('/analytics')
@login_required
def analytics():
    # Data for charts
    risk_counts = {
        'High': RiskProfile.query.filter_by(risk_level='High').count(),
        'Medium': RiskProfile.query.filter_by(risk_level='Medium').count(),
        'Low': RiskProfile.query.filter_by(risk_level='Low').count()
    }
    
    return render_template('analytics.html', risk_counts=risk_counts)
