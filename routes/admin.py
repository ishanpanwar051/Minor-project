from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models_ews import db, User, Student, UserRole, RiskProfile, Intervention, Alert, AlertType, AlertStatus
from services.ml_service import ml_service
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != UserRole.ADMIN:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        grade = request.form.get('grade')
        section = request.form.get('section') # e.g. "Section A"
        parent_email = request.form.get('parent_email')
        
        # Check if student already exists
        if Student.query.filter_by(student_id=student_id).first():
            flash('Student ID already exists.', 'danger')
            return redirect(url_for('admin.add_student'))
        
        if Student.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin.add_student'))
            
        new_student = Student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            grade=grade,
            section=section,
            parent_guardian_email=parent_email,
            enrollment_date=datetime.utcnow()
        )
        
        db.session.add(new_student)
        db.session.commit()
        
        # Initialize empty risk profile
        risk_profile = RiskProfile(
            student_id=new_student.id,
            risk_level='LOW', # Default
            current_risk_score=0
        )
        db.session.add(risk_profile)
        db.session.commit()
        
        flash('Student added successfully!', 'success')
        return redirect(url_for('main.students'))
        
    return render_template('add_student.html')

@admin_bp.route('/intervention/add/<int:student_id>', methods=['POST'])
@login_required
def add_intervention(student_id):
    # Teachers and Admins can add interventions
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER, UserRole.COUNSELOR]:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    type = request.form.get('type')
    title = request.form.get('title')
    description = request.form.get('description')
    
    intervention = Intervention(
        student_id=student_id,
        type=type,
        title=title,
        description=description,
        created_by_id=current_user.id,
        assigned_to_id=current_user.id, # Assign to self by default
        scheduled_date=datetime.utcnow() 
    )
    db.session.add(intervention)
    db.session.commit()
    
    # Send notification email? (logic to be moved to service later)
    
    flash('Intervention recorded.', 'success')
    return redirect(url_for('main.student_detail', id=student_id))

@admin_bp.route('/update_risks')
@login_required
def update_risks():
    if current_user.role != UserRole.ADMIN:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    # Trigger batch risk update using ML service (or rule based if ML fails)
    # This is a stub for calling the ML service batch update
    
    students = Student.query.all()
    count = 0
    for s in students:
        # Get data
        rp = RiskProfile.query.filter_by(student_id=s.id).first()
        data = {
            'attendance_rate': rp.attendance_rate if rp else 100,
            'average_score': rp.average_score if rp else 100,
            'assignment_completion_rate': 80,
            'quiz_average': 75,
            'lms_engagement_score': 50
        }
        
        # Predict
        res = ml_service.predict_risk(data)
        
        if rp:
            rp.ml_risk_probability = res['probability']
            rp.current_risk_score = res['risk_score']
            rp.risk_level = res['risk_level'].upper() # Ensure UPPERCASE for Enum
            rp.last_updated = datetime.utcnow()
            db.session.commit()
            count += 1
            
    flash(f'Updated risk scores for {count} students.', 'success')
    return redirect(url_for('main.dashboard'))
