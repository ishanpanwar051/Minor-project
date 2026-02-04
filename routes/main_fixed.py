from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from models import db, User, Student, Attendance, AcademicRecord, Intervention, RiskProfile
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
    if current_user.role == 'student':
        return redirect(url_for('main.my_profile'))
    elif current_user.role == 'parent':
        return redirect(url_for('main.dashboard'))  # Fallback for parent

    try:
        # KPIS - with safe defaults
        total_students = Student.query.count() or 0
        
        # Check if RiskProfile table exists and has data
        if RiskProfile.query.first():
            high_risk_count = RiskProfile.query.filter_by(risk_level='High').count()
            medium_risk_count = RiskProfile.query.filter_by(risk_level='Medium').count()
        else:
            high_risk_count = 0
            medium_risk_count = 0
        
        # Recent interventions - with safe defaults
        if Intervention.query.first():
            recent_interventions = Intervention.query.order_by(Intervention.date.desc()).limit(5).all()
        else:
            recent_interventions = []
        
        # Recent alerts - using RiskProfile as fallback since Alert might not exist in original models
        if RiskProfile.query.first():
            recent_alerts = RiskProfile.query.filter(RiskProfile.risk_level.in_(['High', 'Medium'])).order_by(RiskProfile.last_updated.desc()).limit(5).all()
        else:
            recent_alerts = []

        return render_template('dashboard_working.html', 
                               total_students=total_students,
                               high_risk_count=high_risk_count,
                               medium_risk_count=medium_risk_count,
                               recent_interventions=recent_interventions,
                               recent_alerts=recent_alerts)
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}")
        # Return a safe fallback dashboard with minimal data
        return render_template('dashboard_working.html', 
                               total_students=0,
                               high_risk_count=0,
                               medium_risk_count=0,
                               recent_interventions=[],
                               recent_alerts=[])

@main_bp.route('/students')
@login_required
def students():
    if current_user.role == 'student':
        abort(403)
        
    risk_filter = request.args.get('risk')
    search_query = request.args.get('search')
    
    query = Student.query
    
    # Join with RiskProfile if it exists
    if RiskProfile.query.first():
        query = query.join(RiskProfile, Student.id == RiskProfile.student_id, isouter=True)
        
        if risk_filter:
            query = query.filter(RiskProfile.risk_level == risk_filter.capitalize())
        
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
    if current_user.role == 'student':
        student_record = Student.query.filter_by(user_id=current_user.id).first()
        if not student_record or student_record.id != id:
            abort(403)
            
    student = Student.query.get_or_404(id)
    
    # Get or create risk profile
    risk_profile = RiskProfile.query.filter_by(student_id=id).first()
    
    # ML Prediction (On demand for demo purposes)
    # In prod, this would be async or pre-calculated
    risk_data = {
        'attendance_rate': risk_profile.attendance_rate if risk_profile else 85,
        'average_score': risk_profile.average_score if risk_profile else 75,
        'assignment_completion_rate': 80, # Placeholder
        'quiz_average': 75, # Placeholder
        'lms_engagement_score': risk_profile.engagement_score if risk_profile else 60
    }
    
    try:
        ml_prediction = ml_service.predict_risk(risk_data)
    except Exception as e:
        current_app.logger.error(f"ML Prediction error: {str(e)}")
        ml_prediction = {'risk_level': 'Medium', 'probability': 0.5, 'risk_score': 50}
    
    records = Attendance.query.filter_by(student_id=id).order_by(Attendance.date.desc()).limit(10).all() if Attendance.query.first() else []
    academic_records = AcademicRecord.query.filter_by(student_id=id).order_by(AcademicRecord.date.desc()).all() if AcademicRecord.query.first() else []
    interventions = Intervention.query.filter_by(student_id=id).order_by(Intervention.date.desc()).all() if Intervention.query.first() else []
    
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
    if current_user.role == 'student':
        abort(403)
        
    risk_counts = {
        'High': RiskProfile.query.filter_by(risk_level='High').count() if RiskProfile.query.first() else 0,
        'Medium': RiskProfile.query.filter_by(risk_level='Medium').count() if RiskProfile.query.first() else 0,
        'Low': RiskProfile.query.filter_by(risk_level='Low').count() if RiskProfile.query.first() else 0
    }
    
    return render_template('analytics.html', risk_counts=risk_counts)

@main_bp.route('/my_profile')
@login_required
def my_profile():
    if current_user.role != 'student':
        return redirect(url_for('main.dashboard'))
        
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        # Try finding by user_id
        student = Student.query.filter_by(user_id=current_user.id).first()
        
    if not student:
        flash('Student record not found.', 'danger')
        return redirect(url_for('auth.logout'))
        
    return redirect(url_for('main.student_detail', id=student.id))
