from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from models_ews import db, User, Student, Attendance, AcademicRecord, Intervention, RiskProfile, UserRole, Alert, SystemLog
from services.ml_service import ml_service
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == UserRole.STUDENT:
        return redirect(url_for('main.my_profile'))
    elif current_user.role == UserRole.PARENT:
        return redirect(url_for('parent.dashboard'))

    # KPIS
    total_students = Student.query.count()
    high_risk_count = RiskProfile.query.filter_by(risk_level='HIGH').count()
    medium_risk_count = RiskProfile.query.filter_by(risk_level='MEDIUM').count()
    
    # Recent interventions
    recent_interventions = Intervention.query.order_by(Intervention.created_at.desc()).limit(5).all()
    
    # Recent alerts
    recent_alerts = Alert.query.filter_by(status='ACTIVE').order_by(Alert.created_at.desc()).limit(5).all()

    return render_template('dashboard.html', 
                           total_students=total_students,
                           high_risk_count=high_risk_count,
                           medium_risk_count=medium_risk_count,
                           recent_interventions=recent_interventions,
                           recent_alerts=recent_alerts)

@main_bp.route('/students')
@login_required
def students():
    if current_user.role == UserRole.STUDENT:
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

@main_bp.route('/student/<int:id>')
@login_required
def student_detail(id):
    # Security Check
    if current_user.role == UserRole.STUDENT:
        student_record = Student.query.filter_by(user_id=current_user.id).first()
        if not student_record or student_record.id != id:
            abort(403)
            
    student = Student.query.get_or_404(id)
    
    # Get or create risk profile
    risk_profile = RiskProfile.query.filter_by(student_id=id).first()
    
    # ML Prediction (On demand for demo purposes)
    # In prod, this would be async or pre-calculated
    risk_data = {
        'attendance_rate': risk_profile.attendance_rate if risk_profile else 100,
        'average_score': risk_profile.average_score if risk_profile else 100,
        'assignment_completion_rate': 80, # Placeholder
        'quiz_average': 75, # Placeholder
        'lms_engagement_score': risk_profile.engagement_score if risk_profile else 50
    }
    ml_prediction = ml_service.predict_risk(risk_data)
    
    records = Attendance.query.filter_by(student_id=id).order_by(Attendance.date.desc()).limit(10).all()
    academic_records = AcademicRecord.query.filter_by(student_id=id).order_by(AcademicRecord.date.desc()).all()
    interventions = Intervention.query.filter_by(student_id=id).order_by(Intervention.created_at.desc()).all()
    
    return render_template('student_detail.html', 
                           student=student, 
                           risk=risk_profile,
                           ml_prediction=ml_prediction,
                           attendance=records,
                           grades=academic_records,
                           interventions=interventions)

@main_bp.route('/analytics')
@login_required
def analytics():
    if current_user.role == UserRole.STUDENT:
        abort(403)
        
    risk_counts = {
        'High': RiskProfile.query.filter_by(risk_level='HIGH').count(),
        'Medium': RiskProfile.query.filter_by(risk_level='MEDIUM').count(),
        'Low': RiskProfile.query.filter_by(risk_level='LOW').count()
    }
    
    return render_template('analytics.html', risk_counts=risk_counts)

@main_bp.route('/my_profile')
@login_required
def my_profile():
    if current_user.role != UserRole.STUDENT:
        return redirect(url_for('main.dashboard'))
        
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        # Try finding by user_id
        student = Student.query.filter_by(user_id=current_user.id).first()
        
    if not student:
        flash('Student record not found.', 'danger')
        return redirect(url_for('auth.logout'))
        
    return redirect(url_for('main.student_detail', id=student.id))
