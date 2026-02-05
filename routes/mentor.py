"""
Mentor Assignment Routes for EduGuard System
Handles mentor-student assignment and tracking
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from models import db, Student, User, MentorAssignment

mentor_bp = Blueprint('mentor', __name__)

@mentor_bp.route('/mentor')
@login_required
def mentor_dashboard():
    """Mentor dashboard"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        # Get mentor's assigned students
        assigned_students = db.session.query(Student, MentorAssignment).join(
            MentorAssignment
        ).filter(
            MentorAssignment.mentor_id == current_user.id,
            MentorAssignment.status == 'Active'
        ).all()
        
        # Get mentor statistics
        total_assignments = MentorAssignment.query.filter_by(mentor_id=current_user.id).count()
        active_assignments = MentorAssignment.query.filter_by(
            mentor_id=current_user.id, 
            status='Active'
        ).count()
        
        return render_template('mentor/dashboard.html',
                               assigned_students=assigned_students,
                               total_assignments=total_assignments,
                               active_assignments=active_assignments)
    except Exception as e:
        flash(f'Error loading mentor dashboard: {str(e)}', 'danger')
        return render_template('mentor/dashboard.html')

@mentor_bp.route('/mentor/assign', methods=['GET', 'POST'])
@login_required
def assign_mentor():
    """Assign mentor to student (Admin only)"""
    if current_user.role != 'admin':
        abort(403)
    
    if request.method == 'POST':
        try:
            mentor_id = request.form.get('mentor_id')
            student_id = request.form.get('student_id')
            notes = request.form.get('notes')
            
            # Check if assignment already exists
            existing_assignment = MentorAssignment.query.filter_by(
                mentor_id=mentor_id,
                student_id=student_id,
                status='Active'
            ).first()
            
            if existing_assignment:
                flash('This mentor is already assigned to this student', 'warning')
            else:
                # Create new assignment
                assignment = MentorAssignment(
                    mentor_id=mentor_id,
                    student_id=student_id,
                    notes=notes
                )
                
                db.session.add(assignment)
                db.session.commit()
                
                flash('Mentor assigned successfully!', 'success')
                return redirect(url_for('mentor.assign_mentor'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error assigning mentor: {str(e)}', 'danger')
    
    # Get data for dropdowns
    mentors = User.query.filter(User.role.in_(['admin', 'faculty'])).all()
    students = Student.query.order_by(Student.last_name).all()
    
    return render_template('mentor/assign.html', mentors=mentors, students=students)

@mentor_bp.route('/mentor/assignments')
@login_required
def view_assignments():
    """View all mentor assignments (Admin only)"""
    if current_user.role != 'admin':
        abort(403)
    
    try:
        assignments = db.session.query(
            MentorAssignment, Student, User
        ).join(
            Student, MentorAssignment.student_id == Student.id
        ).join(
            User, MentorAssignment.mentor_id == User.id
        ).order_by(MentorAssignment.assignment_date.desc()).all()
        
        return render_template('mentor/assignments.html', assignments=assignments)
    except Exception as e:
        flash(f'Error loading assignments: {str(e)}', 'danger')
        return render_template('mentor/assignments.html')

@mentor_bp.route('/mentor/student/<int:student_id>')
@login_required
def mentor_student_detail(student_id):
    """Mentor view of assigned student details"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    # Check if mentor is assigned to this student
    assignment = MentorAssignment.query.filter_by(
        mentor_id=current_user.id,
        student_id=student_id,
        status='Active'
    ).first()
    
    if not assignment and current_user.role == 'faculty':
        abort(403)
    
    student = Student.query.get_or_404(student_id)
    
    # Get student's data
    from models import Attendance, AcademicRecord, Intervention
    attendance_records = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).limit(10).all()
    academic_records = AcademicRecord.query.filter_by(student_id=student_id).order_by(AcademicRecord.exam_date.desc()).limit(10).all()
    interventions = Intervention.query.filter_by(student_id=student_id).order_by(Intervention.date.desc()).limit(5).all()
    
    return render_template('mentor/student_detail.html',
                               student=student,
                               assignment=assignment,
                               attendance_records=attendance_records,
                               academic_records=academic_records,
                               interventions=interventions)

@mentor_bp.route('/mentor/update_progress/<int:assignment_id>', methods=['POST'])
@login_required
def update_progress():
    """Update mentor progress notes"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        assignment = MentorAssignment.query.get_or_404(assignment_id)
        
        # Check permissions
        if current_user.role == 'faculty' and assignment.mentor_id != current_user.id:
            abort(403)
        
        notes = request.form.get('notes')
        status = request.form.get('status')
        
        assignment.notes = notes
        assignment.status = status
        assignment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Progress updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@mentor_bp.route('/mentor/remove_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def remove_assignment():
    """Remove mentor assignment (Admin only)"""
    if current_user.role != 'admin':
        abort(403)
    
    try:
        assignment = MentorAssignment.query.get_or_404(assignment_id)
        assignment.status = 'Inactive'
        assignment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Mentor assignment removed successfully!', 'success')
        return redirect(url_for('mentor.view_assignments'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing assignment: {str(e)}', 'danger')
        return redirect(url_for('mentor.view_assignments'))

# Helper functions
def get_mentor_statistics(mentor_id):
    """Get statistics for a specific mentor"""
    try:
        total = MentorAssignment.query.filter_by(mentor_id=mentor_id).count()
        active = MentorAssignment.query.filter_by(mentor_id=mentor_id, status='Active').count()
        completed = MentorAssignment.query.filter_by(mentor_id=mentor_id, status='Completed').count()
        
        return {
            'total': total,
            'active': active,
            'completed': completed,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }
    except Exception as e:
        return {'total': 0, 'active': 0, 'completed': 0, 'completion_rate': 0}
