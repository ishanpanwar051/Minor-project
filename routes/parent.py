from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models_ews import Student, UserRole, RiskProfile, Attendance

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != UserRole.PARENT:
        return redirect(url_for('main.dashboard'))

    # Find students linked to this parent (by email for now, or we can add a relationship table later)
    # The models_ews.py has `parent_guardian_email` in Student.
    children = Student.query.filter_by(parent_guardian_email=current_user.email).all()
    
    return render_template('parent_dashboard.html', children=children)

@parent_bp.route('/child/<int:student_id>')
@login_required
def child_detail(student_id):
    if current_user.role != UserRole.PARENT:
        abort(403)
        
    student = Student.query.get_or_404(student_id)
    
    # Verify this is their child
    if student.parent_guardian_email != current_user.email:
        abort(403)
        
    risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
    attendance = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).limit(5).all()
    
    return render_template('child_detail.html', student=student, risk=risk_profile, attendance=attendance)
