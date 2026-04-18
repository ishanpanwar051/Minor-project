#!/usr/bin/env python3
"""
Student Routes with Complete RBAC Protection and Data Isolation
Production-ready student panel with role-based access control
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Student, Attendance, RiskProfile, Alert
from models_support import StudentGoal, MoodLog
from rbac_system import student_required, student_data_access, get_student_for_current_user, validate_student_access
from enhanced_ai_info import student_ai_info
from datetime import datetime, date, timedelta

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/')
@student_bp.route('/dashboard')
@student_required
def dashboard():
    """
    Student Dashboard - Personalized view with complete data isolation
    Only accessible by logged-in students
    """
    # Get current student's profile (data isolation enforced)
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found. Please contact administrator.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get student's personal data only
    attendance_records = Attendance.query.filter_by(student_id=student.id)\
        .order_by(desc(Attendance.date)).limit(10).all()
    
    # Get student's risk profile
    risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
    
    # Get student's active alerts
    alerts = Alert.query.filter_by(student_id=student.id, status='Active')\
        .order_by(desc(Alert.created_at)).limit(5).all()
    
    # Get student's goals
    active_goals = StudentGoal.query.filter_by(student_id=student.id, status='Active')\
        .order_by(desc(StudentGoal.created_at)).limit(5).all()
    
    # Get student's mood logs
    recent_moods = MoodLog.query.filter_by(student_id=student.id)\
        .order_by(desc(MoodLog.log_date)).limit(7).all()
    
    # Get AI insights (personalized)
    ai_info = student_ai_info.get_student_comprehensive_info(student.id)
    
    return render_template('student/dashboard.html',
                         student=student,
                         attendance_records=attendance_records,
                         risk_profile=risk_profile,
                         alerts=alerts,
                         active_goals=active_goals,
                         recent_moods=recent_moods,
                         ai_info=ai_info)

@student_bp.route('/profile')
@student_required
def profile():
    """
    Student Profile - View and edit personal information
    Only student's own profile
    """
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found. Please contact administrator.', 'danger')
        return redirect(url_for('auth.logout'))
    
    return render_template('student/profile.html', student=student)

@student_bp.route('/profile/edit', methods=['GET', 'POST'])
@student_required
def edit_profile():
    """
    Edit student profile - Only own profile
    """
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found. Please contact administrator.', 'danger')
        return redirect(url_for('auth.logout'))
    
    if request.method == 'POST':
        # Get form data (only allow editing certain fields)
        student.parent_name = request.form.get('parent_name', '').strip()
        student.parent_email = request.form.get('parent_email', '').strip()
        student.parent_phone = request.form.get('parent_phone', '').strip()
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('student.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'danger')
            print(f"Profile update error: {e}")
    
    return render_template('student/edit_profile.html', student=student)

@student_bp.route('/attendance')
@student_required
def attendance():
    """
    View attendance records - Only student's own attendance
    """
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found. Please contact administrator.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get student's attendance only
    attendance_records = Attendance.query.filter_by(student_id=student.id)\
        .order_by(desc(Attendance.date))\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate attendance statistics
    total_records = Attendance.query.filter_by(student_id=student.id).count()
    present_records = Attendance.query.filter_by(student_id=student.id, status='Present').count()
    attendance_rate = (present_records / total_records * 100) if total_records > 0 else 0
    
    return render_template('student/attendance.html',
                         attendance_records=attendance_records,
                         attendance_rate=round(attendance_rate, 1),
                         total_records=total_records,
                         present_records=present_records)

@student_bp.route('/goals')
@student_required
def goals():
    """
    View and manage personal goals
    """
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found. Please contact administrator.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get student's goals only
    active_goals = StudentGoal.query.filter_by(student_id=student.id, status='Active')\
        .order_by(desc(StudentGoal.created_at)).all()
    
    completed_goals = StudentGoal.query.filter_by(student_id=student.id, status='Completed')\
        .order_by(desc(StudentGoal.updated_at)).limit(10).all()
    
    abandoned_goals = StudentGoal.query.filter_by(student_id=student.id, status='Abandoned')\
        .order_by(desc(StudentGoal.updated_at)).limit(5).all()
    
    return render_template('student/goals.html',
                         student=student,
                         active_goals=active_goals,
                         completed_goals=completed_goals,
                         abandoned_goals=abandoned_goals)

@student_bp.route('/goals/add', methods=['POST'])
@student_required
def add_goal():
    """
    Add new personal goal
    """
    student = get_student_for_current_user()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    target_date_str = request.form.get('target_date', '').strip()
    
    if not title:
        if request.is_json:
            return jsonify({'error': 'Goal title is required'}), 400
        flash('Goal title is required', 'danger')
        return redirect(url_for('student.goals'))
    
    try:
        target_date = None
        if target_date_str:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        
        goal = StudentGoal(
            student_id=student.id,  # Ensure only current student's goal
            title=title,
            description=description,
            target_date=target_date
        )
        
        db.session.add(goal)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'goal_id': goal.id})
        
        flash('Goal added successfully!', 'success')
        return redirect(url_for('student.goals'))
        
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Failed to add goal'}), 500
        flash('Error adding goal. Please try again.', 'danger')
        print(f"Goal addition error: {e}")
        return redirect(url_for('student.goals'))

@student_bp.route('/goals/<int:goal_id>/update', methods=['POST'])
@student_required
def update_goal(goal_id):
    """
    Update personal goal - Only own goals
    """
    student = get_student_for_current_user()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Get goal and verify ownership
    goal = StudentGoal.query.filter_by(id=goal_id, student_id=student.id).first()
    if not goal:
        if request.is_json:
            return jsonify({'error': 'Goal not found or access denied'}), 404
        flash('Goal not found or access denied', 'danger')
        return redirect(url_for('student.goals'))
    
    # Update goal
    action = request.form.get('action', '')
    
    try:
        if action == 'complete':
            goal.status = 'Completed'
            goal.progress = 100
            goal.updated_at = datetime.utcnow()
            flash('Goal marked as completed!', 'success')
        elif action == 'abandon':
            goal.status = 'Abandoned'
            goal.updated_at = datetime.utcnow()
            flash('Goal abandoned', 'info')
        elif action == 'update_progress':
            progress = int(request.form.get('progress', 0))
            goal.progress = max(0, min(100, progress))
            goal.updated_at = datetime.utcnow()
            flash('Goal progress updated!', 'success')
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'status': goal.status, 'progress': goal.progress})
        
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Failed to update goal'}), 500
        flash('Error updating goal. Please try again.', 'danger')
        print(f"Goal update error: {e}")
    
    return redirect(url_for('student.goals'))

@student_bp.route('/mood')
@student_required
def mood():
    """
    View mood tracking history
    """
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found. Please contact administrator.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get student's mood logs only
    mood_logs = MoodLog.query.filter_by(student_id=student.id)\
        .order_by(desc(MoodLog.log_date)).limit(30).all()
    
    # Calculate mood statistics
    total_moods = len(mood_logs)
    avg_mood = sum(log.mood_score for log in mood_logs) / total_moods if total_moods > 0 else 0
    
    return render_template('student/mood.html',
                         mood_logs=mood_logs,
                         avg_mood=round(avg_mood, 1),
                         total_moods=total_moods)

@student_bp.route('/mood/add', methods=['POST'])
@student_required
def add_mood():
    """
    Add mood entry
    """
    student = get_student_for_current_user()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    mood_score = request.form.get('mood_score', type=int)
    note = request.form.get('note', '').strip()
    
    if not mood_score or mood_score < 1 or mood_score > 5:
        if request.is_json:
            return jsonify({'error': 'Valid mood score (1-5) required'}), 400
        flash('Valid mood score (1-5) required', 'danger')
        return redirect(url_for('student.mood'))
    
    try:
        # Check if mood already exists for today
        today_mood = MoodLog.query.filter_by(
            student_id=student.id,
            log_date=date.today()
        ).first()
        
        if today_mood:
            # Update existing mood
            today_mood.mood_score = mood_score
            today_mood.note = note
            today_mood.logged_at = datetime.utcnow()
        else:
            # Create new mood entry
            mood = MoodLog(
                student_id=student.id,  # Ensure only current student's mood
                mood_score=mood_score,
                note=note
            )
            db.session.add(mood)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True})
        
        flash('Mood logged successfully!', 'success')
        return redirect(url_for('student.mood'))
        
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Failed to log mood'}), 500
        flash('Error logging mood. Please try again.', 'danger')
        print(f"Mood logging error: {e}")
        return redirect(url_for('student.mood'))

@student_bp.route('/ai-insights')
@student_required
def ai_insights():
    """
    View personalized AI insights and recommendations
    """
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found. Please contact administrator.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get comprehensive AI analysis
    ai_info = student_ai_info.get_student_comprehensive_info(student.id)
    
    return render_template('student/ai_insights.html',
                         student=student,
                         ai_info=ai_info)

@student_bp.route('/api/dashboard-stats')
@student_required
def api_dashboard_stats():
    """
    API endpoint for dashboard statistics - Only student's own data
    """
    student = get_student_for_current_user()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Get student's personal statistics
    total_attendance = Attendance.query.filter_by(student_id=student.id).count()
    present_attendance = Attendance.query.filter_by(student_id=student.id, status='Present').count()
    attendance_rate = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0
    
    active_goals = StudentGoal.query.filter_by(student_id=student.id, status='Active').count()
    completed_goals = StudentGoal.query.filter_by(student_id=student.id, status='Completed').count()
    
    risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
    
    stats = {
        'attendance_rate': round(attendance_rate, 1),
        'total_attendance': total_attendance,
        'present_attendance': present_attendance,
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'gpa': student.gpa,
        'risk_level': risk_profile.risk_level if risk_profile else 'Low',
        'risk_score': risk_profile.risk_score if risk_profile else 0
    }
    
    return jsonify(stats)

# Error handlers for student blueprint
@student_bp.errorhandler(403)
def forbidden(error):
    flash('Access denied. Student privileges required.', 'danger')
    return redirect(url_for('auth.login'))

@student_bp.errorhandler(404)
def not_found(error):
    return render_template('student/404.html'), 404
