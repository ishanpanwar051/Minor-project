"""
Counselling Routes for EduGuard System
Handles counselling session management for students
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import db, Student, Counselling, User

counselling_bp = Blueprint('counselling', __name__)

@counselling_bp.route('/counselling')
@login_required
def counselling_dashboard():
    """Main counselling dashboard"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        # Get upcoming counselling sessions
        upcoming_sessions = Counselling.query.filter(
            Counselling.date >= date.today(),
            Counselling.status.in_(['Scheduled', 'In Progress'])
        ).order_by(Counselling.date.asc()).all()
        
        # Get recent completed sessions
        recent_sessions = Counselling.query.filter(
            Counselling.status == 'Completed'
        ).order_by(Counselling.date.desc()).limit(10).all()
        
        # Get counselling statistics
        total_sessions = Counselling.query.count()
        completed_sessions = Counselling.query.filter_by(status='Completed').count()
        pending_sessions = Counselling.query.filter(Counselling.status.in_(['Scheduled', 'In Progress'])).count()
        
        return render_template('counselling/dashboard.html',
                               upcoming_sessions=upcoming_sessions,
                               recent_sessions=recent_sessions,
                               total_sessions=total_sessions,
                               completed_sessions=completed_sessions,
                               pending_sessions=pending_sessions)
    except Exception as e:
        flash(f'Error loading counselling dashboard: {str(e)}', 'danger')
        return render_template('counselling/dashboard.html')

@counselling_bp.route('/counselling/schedule', methods=['GET', 'POST'])
@login_required
def schedule_counselling():
    """Schedule new counselling session"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            counselling_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            counselling_type = request.form.get('type')
            remarks = request.form.get('remarks')
            follow_up_date = None
            if request.form.get('follow_up_date'):
                follow_up_date = datetime.strptime(request.form.get('follow_up_date'), '%Y-%m-%d').date()
            
            # Create counselling session
            counselling = Counselling(
                student_id=student_id,
                date=counselling_date,
                counselling_type=counselling_type,
                remarks=remarks,
                follow_up_date=follow_up_date,
                counsellor_id=current_user.id
            )
            
            db.session.add(counselling)
            db.session.commit()
            
            flash('Counselling session scheduled successfully!', 'success')
            return redirect(url_for('counselling.counselling_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error scheduling counselling: {str(e)}', 'danger')
    
    # Get students for dropdown
    students = Student.query.order_by(Student.last_name).all()
    return render_template('counselling/schedule.html', students=students)

@counselling_bp.route('/counselling/session/<int:id>')
@login_required
def view_counselling_session(id):
    """View specific counselling session"""
    counselling = Counselling.query.get_or_404(id)
    
    # Check permissions
    if current_user.role == 'student' and counselling.student_id != current_user.student_profile.id:
        abort(403)
    
    return render_template('counselling/session.html', counselling=counselling)

@counselling_bp.route('/counselling/session/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_counselling_session(id):
    """Edit counselling session"""
    counselling = Counselling.query.get_or_404(id)
    
    # Check permissions
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    if request.method == 'POST':
        try:
            counselling.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            counselling.counselling_type = request.form.get('type')
            counselling.remarks = request.form.get('remarks')
            counselling.status = request.form.get('status')
            
            if request.form.get('follow_up_date'):
                counselling.follow_up_date = datetime.strptime(request.form.get('follow_up_date'), '%Y-%m-%d').date()
            
            counselling.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Counselling session updated successfully!', 'success')
            return redirect(url_for('counselling.view_counselling_session', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating counselling: {str(e)}', 'danger')
    
    return render_template('counselling/edit.html', counselling=counselling)

@counselling_bp.route('/counselling/session/<int:id>/complete', methods=['POST'])
@login_required
def complete_counselling_session(id):
    """Mark counselling session as completed"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        counselling = Counselling.query.get_or_404(id)
        counselling.status = 'Completed'
        counselling.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Counselling session marked as completed!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@counselling_bp.route('/counselling/student/<int:student_id>')
@login_required
def student_counselling_history(student_id):
    """View counselling history for a student"""
    student = Student.query.get_or_404(student_id)
    
    # Check permissions
    if current_user.role == 'student' and student_id != current_user.student_profile.id:
        abort(403)
    
    counselling_sessions = Counselling.query.filter_by(student_id=student_id).order_by(Counselling.date.desc()).all()
    
    return render_template('counselling/student_history.html', 
                               student=student, 
                               counselling_sessions=counselling_sessions)

@counselling_bp.route('/counselling/calendar')
@login_required
def counselling_calendar():
    """Calendar view of counselling sessions"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    # Get all sessions for the month
    year = request.args.get('year', datetime.now().year)
    month = request.args.get('month', datetime.now().month)
    
    sessions = Counselling.query.filter(
        db.extract('year', Counselling.date) == year,
        db.extract('month', Counselling.date) == month
    ).all()
    
    return render_template('counselling/calendar.html', 
                               sessions=sessions, 
                               year=year, 
                               month=month)

# Helper functions
def get_counselling_statistics():
    """Get counselling statistics for dashboard"""
    try:
        total = Counselling.query.count()
        completed = Counselling.query.filter_by(status='Completed').count()
        by_type = db.session.query(
            Counselling.counselling_type,
            db.func.count(Counselling.id)
        ).group_by(Counselling.counselling_type).all()
        
        return {
            'total': total,
            'completed': completed,
            'completion_rate': (completed / total * 100) if total > 0 else 0,
            'by_type': dict(by_type)
        }
    except Exception as e:
        return {'total': 0, 'completed': 0, 'completion_rate': 0, 'by_type': {}}
