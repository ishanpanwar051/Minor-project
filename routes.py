from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student, Attendance, AcademicRecord, Intervention, RiskProfile
from utils import update_student_risk
from datetime import datetime
from functools import wraps

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- Authentication Routes ---
@auth.route('/register', methods=['GET', 'POST'])
@login_required
@admin_required
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Validation for Student role
        if role == 'student':
            student_record = Student.query.filter_by(email=email).first()
            if not student_record:
                flash(f'No Student record found with email {email}. Please create the student profile first.', 'warning')
                return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('User created successfully.', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('main.my_profile'))
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        
        # Log successful login
        current_app.logger.info(f'User {user.email} logged in successfully')
        
        if user.role == 'student':
            return redirect(url_for('main.my_profile'))
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
    if current_user.role == 'student':
        return redirect(url_for('main.my_profile'))

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
    if current_user.role == 'student':
        abort(403)
        
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

@main.route('/add_student', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        semester = request.form.get('semester')
        
        # Check if student already exists
        if Student.query.filter_by(student_id=student_id).first():
            flash('Student ID already exists.', 'danger')
            return redirect(url_for('main.add_student'))
        
        if Student.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('main.add_student'))
            
        new_student = Student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            semester=semester,
            enrollment_date=datetime.utcnow()
        )
        
        db.session.add(new_student)
        db.session.commit()
        
        # Initialize empty risk profile
        risk_profile = update_student_risk(new_student)
        
        # Send email alert if high risk (only if email is configured)
        if risk_profile.risk_level == 'High' and current_app.config.get('MAIL_USERNAME'):
            try:
                from email_service import send_risk_alert_email
                send_risk_alert_email(new_student, risk_profile)
            except Exception as e:
                current_app.logger.error(f"Failed to send risk alert: {str(e)}")
        
        flash('Student added successfully! You can now create a login for them.', 'success')
        return redirect(url_for('main.students'))
        
    return render_template('add_student.html')

@main.route('/my_profile')
@login_required
def my_profile():
    if current_user.role != 'student':
        return redirect(url_for('main.dashboard'))
        
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        flash('Student record not found for this user.', 'danger')
        return redirect(url_for('auth.logout'))
        
    # Use existing detail view logic or render a specific student dashboard
    return render_template('student_dashboard.html', student=student, risk=update_student_risk(student))

@main.route('/student/<int:id>')
@login_required
def student_detail(id):
    # Security Check: Students can only view their own profile
    if current_user.role == 'student':
        # Find the student record linked to this user
        student_record = Student.query.filter_by(email=current_user.email).first()
        if not student_record or student_record.id != id:
            abort(403)
            
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
    
    # Send notification email (only if email is configured)
    if current_app.config.get('MAIL_USERNAME'):
        try:
            from email_service import send_intervention_notification
            student = Student.query.get(id)
            send_intervention_notification(student, intervention)
        except Exception as e:
            current_app.logger.error(f"Failed to send intervention notification: {str(e)}")
    
    flash('Intervention recorded successfully.', 'success')
    return redirect(url_for('main.student_detail', id=id))

@main.route('/analytics')
@login_required
def analytics():
    if current_user.role == 'student':
        abort(403)
        
    # Data for charts
    risk_counts = {
        'High': RiskProfile.query.filter_by(risk_level='High').count(),
        'Medium': RiskProfile.query.filter_by(risk_level='Medium').count(),
        'Low': RiskProfile.query.filter_by(risk_level='Low').count()
    }
    
    return render_template('analytics.html', risk_counts=risk_counts)
