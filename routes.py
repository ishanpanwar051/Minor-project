"""
EduGuard Routes
Clean, consolidated routing
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student, Attendance, RiskProfile, Counselling, MentorAssignment, Alert
from datetime import datetime, date, timedelta
import random

# Create blueprint
main_bp = Blueprint('main', __name__)

# Helper functions
def admin_required(f):
    """Decorator for admin-only access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def faculty_required(f):
    """Decorator for faculty/admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'faculty']:
            flash('Faculty access required', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@main_bp.route('/')
def index():
    """Home page - redirect based on auth status"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = bool(request.form.get('remember'))
            
            if not email or not password:
                flash('Please enter email and password', 'danger')
                return render_template('login.html')
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash('Login successful!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid email or password', 'danger')
                
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
    
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    """Logout"""
    try:
        logout_user()
        flash('You have been logged out', 'success')
    except Exception as e:
        flash(f'Logout error: {str(e)}', 'danger')
    
    return redirect(url_for('main.login'))

# Dashboard routes
@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    try:
        # Get statistics
        total_students = Student.query.count()
        
        # Calculate risk statistics
        risk_stats = {
            'low': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Low').count(),
            'medium': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Medium').count(),
            'high': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'High').count(),
            'critical': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Critical').count()
        }
        
        high_risk_students = risk_stats['high'] + risk_stats['critical']
        
        # Top risky students for cards (sorted: Critical/High then score)
        risky_students = Student.query.join(RiskProfile).order_by(
            db.case(
                (RiskProfile.risk_level == 'Critical', 0),
                (RiskProfile.risk_level == 'High', 1),
                (RiskProfile.risk_level == 'Medium', 2),
                else_=3
            ),
            RiskProfile.risk_score.desc()
        ).limit(8).all()
        
        # Calculate attendance rate
        recent_attendance = Attendance.query.filter(
            Attendance.date >= date.today() - timedelta(days=30)
        ).all()
        
        if recent_attendance:
            attendance_rate = (len([a for a in recent_attendance if a.status == 'Present']) / len(recent_attendance)) * 100
        else:
            attendance_rate = 0
        
        # Get recent alerts
        recent_alerts = Alert.query.filter_by(status='Active').order_by(Alert.created_at.desc()).limit(5).all()
        
        return render_template('dashboard.html',
                             total_students=total_students,
                             at_risk_students=high_risk_students,
                             avg_attendance=round(attendance_rate, 1),
                             risk_stats=risk_stats,
                             recent_alerts=recent_alerts,
                             risky_students=risky_students)
        
    except Exception as e:
        flash(f'Dashboard error: {str(e)}', 'danger')
        return render_template('dashboard.html',
                             total_students=0,
                             at_risk_students=0,
                             avg_attendance=0,
                             risk_stats={'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
                             recent_alerts=[])

@main_bp.route('/add_student', methods=['GET', 'POST'])
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
        risk_profile = RiskProfile(
            student_id=new_student.id,
            risk_score=0.0,
            risk_level='Low',
            attendance_rate=100.0,
            academic_performance=100.0
        )
        db.session.add(risk_profile)
        db.session.commit()
        
        flash('Student added successfully! You can now create a login for them.', 'success')
        return redirect(url_for('main.students'))
        
    return render_template('add_student.html')

@main_bp.route('/students')
@login_required
@faculty_required
def students():
    """Students list page"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        query = Student.query
        
        if search:
            query = query.filter(
                Student.first_name.contains(search) |
                Student.last_name.contains(search) |
                Student.student_id.contains(search) |
                Student.email.contains(search)
            )
        
        students = query.paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('students.html', students=students, search=search)
        
    except Exception as e:
        flash(f'Students error: {str(e)}', 'danger')
        return render_template('students.html', students=None, search='')

@main_bp.route('/student/<int:student_id>')
@login_required
@faculty_required
def student_detail(student_id):
    """Student detail page"""
    try:
        student = Student.query.get_or_404(student_id)
        
        # Get attendance data
        attendance_records = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).limit(30).all()
        
        # Calculate attendance rate
        if attendance_records:
            attendance_rate = (len([a for a in attendance_records if a.status == 'Present']) / len(attendance_records)) * 100
        else:
            attendance_rate = 0
        
        # Get risk profile
        risk_profile = RiskProfile.query.filter_by(student_id=student_id).first()
        
        # Get counselling sessions
        counselling_sessions = Counselling.query.filter_by(student_id=student_id).order_by(Counselling.session_date.desc()).limit(5).all()
        
        # Get alerts
        alerts = Alert.query.filter_by(student_id=student_id).order_by(Alert.created_at.desc()).limit(5).all()
        
        return render_template('student_detail.html',
                             student=student,
                             attendance_records=attendance_records,
                             attendance_rate=round(attendance_rate, 1),
                             risk_profile=risk_profile,
                             counselling_sessions=counselling_sessions,
                             alerts=alerts)
        
    except Exception as e:
        flash(f'Student detail error: {str(e)}', 'danger')
        return redirect(url_for('main.students'))

@main_bp.route('/attendance')
@login_required
@faculty_required
def attendance():
    """Attendance management page"""
    try:
        date_filter = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        
        attendance_records = Attendance.query.filter_by(date=date.fromisoformat(date_filter)).all()
        
        return render_template('attendance.html', 
                             attendance_records=attendance_records,
                             selected_date=date_filter)
        
    except Exception as e:
        flash(f'Attendance error: {str(e)}', 'danger')
        return render_template('attendance.html', attendance_records=[], selected_date=date.today().strftime('%Y-%m-%d'))

@main_bp.route('/risk')
@login_required
@faculty_required
def risk():
    """Risk management page"""
    try:
        # Get all students with risk profiles
        students_with_risk = Student.query.join(RiskProfile).all()
        
        # Filter by risk level if specified
        risk_filter = request.args.get('risk_level', '')
        if risk_filter:
            students_with_risk = [s for s in students_with_risk if s.risk_profile.risk_level == risk_filter]
        
        return render_template('risk.html', students=students_with_risk, risk_filter=risk_filter)
        
    except Exception as e:
        flash(f'Risk analysis error: {str(e)}', 'danger')
        return render_template('risk.html', students=[], risk_filter='')

@main_bp.route('/admin')
@login_required
@admin_required
def admin():
    """Admin panel"""
    try:
        # Get system statistics
        stats = {
            'total_users': User.query.count(),
            'total_students': Student.query.count(),
            'active_alerts': Alert.query.filter_by(status='Active').count(),
            'pending_counselling': Counselling.query.filter_by(status='Scheduled').count()
        }
        
        # Get recent users
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        return render_template('admin.html', stats=stats, recent_users=recent_users)
        
    except Exception as e:
        flash(f'Admin panel error: {str(e)}', 'danger')
        return render_template('admin.html', stats={}, recent_users=[])

# API routes for AJAX
@main_bp.route('/api/update_risk/<int:student_id>')
@login_required
@faculty_required
def update_risk(student_id):
    """Update student risk profile based on real data"""
    try:
        student = Student.query.get_or_404(student_id)
        risk_profile = RiskProfile.query.filter_by(student_id=student_id).first()
        
        if not risk_profile:
            risk_profile = RiskProfile(student_id=student_id)
            db.session.add(risk_profile)
        
        # Update risk score using the holistic model method
        risk_profile.update_risk_score()
        
        # Generate Alert if High or Critical
        if risk_profile.risk_level in ['High', 'Critical']:
            # Check if active alert already exists
            existing_alert = Alert.query.filter_by(
                student_id=student_id, 
                status='Active',
                alert_type='Risk Level'
            ).first()
            
            if not existing_alert:
                new_alert = Alert(
                    student_id=student_id,
                    alert_type='Risk Level',
                    severity=risk_profile.risk_level,
                    title=f'{risk_profile.risk_level} Risk Detected',
                    description=f'Student risk score reached {risk_profile.risk_score:.1f}. Factors: Academic={risk_profile.academic_performance}%, Attendance={risk_profile.attendance_rate}%',
                    status='Active'
                )
                db.session.add(new_alert)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'risk_score': round(risk_profile.risk_score, 1),
            'risk_level': risk_profile.risk_level,
            'reasons': risk_profile.risk_reasons
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/api/auto_update_risk_all')
@login_required
@faculty_required
def auto_update_risk_all():
    try:
        students = Student.query.all()
        summary = {'updated': 0, 'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for s in students:
            rp = RiskProfile.query.filter_by(student_id=s.id).first()
            if not rp:
                rp = RiskProfile(student_id=s.id)
                db.session.add(rp)
            rp.update_risk_score()
            summary['updated'] += 1
            if rp.risk_level == 'Low':
                summary['low'] += 1
            elif rp.risk_level == 'Medium':
                summary['medium'] += 1
            elif rp.risk_level == 'High':
                summary['high'] += 1
            elif rp.risk_level == 'Critical':
                summary['critical'] += 1
        db.session.commit()
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
