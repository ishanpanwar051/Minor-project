from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Student
from models_support import StudentGoal, MoodLog
from enhanced_ai_info import student_ai_info
from datetime import datetime, date, timedelta
import sqlalchemy as sa

support_bp = Blueprint('support', __name__, url_prefix='/support')

@support_bp.route('/dashboard')
@login_required
def dashboard():
    """Combined support dashboard with goals and mood - STUDENT ONLY"""
    # STRICT: Only students can access this route
    if current_user.role != 'student':
        flash('Access denied. This area is for students only.', 'danger')
        return redirect(url_for('main.login'))  # Send back to login, not dashboard
    
    # Find student by user_id first
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        # Fallback: try email matching
        student = Student.query.filter_by(email=current_user.email).first()
        if not student:
            flash('Student profile not found. Please contact administrator.', 'danger')
            return redirect(url_for('main.login'))
    
    # Additional security: Verify this student belongs to current user
    if student.user_id != current_user.id:
        flash('Access denied. Invalid student assignment.', 'danger')
        return redirect(url_for('main.login'))
    
    # Get motivational quote based on date
    quotes = [
        "Education is the most powerful weapon which you can use to change the world. - Nelson Mandela",
        "The secret of getting ahead is getting started. - Mark Twain",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "It does not matter how slowly you go as long as you do not stop. - Confucius",
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Believe you can and you're halfway there. - Theodore Roosevelt",
        "Your limitation—it's only your imagination.",
        "Great things never come from comfort zones.",
        "Dream it. Wish it. Do it."
    ]
    
    today_index = date.today().toordinal() % len(quotes)
    todays_quote = quotes[today_index]
    
    # Get active goals
    active_goals = StudentGoal.query.filter_by(
        student_id=student.id, 
        status='Active'
    ).order_by(StudentGoal.target_date.asc()).all()
    
    # Get mood data for last 7 days
    seven_days_ago = date.today() - timedelta(days=7)
    mood_logs = MoodLog.query.filter(
        MoodLog.student_id == student.id,
        MoodLog.log_date >= seven_days_ago
    ).order_by(MoodLog.log_date.asc()).all()
    
    # Create mood data for last 7 days
    mood_data = {}
    for i in range(7):
        check_date = date.today() - timedelta(days=i)
        mood_data[check_date] = None
    
    for log in mood_logs:
        mood_data[log.log_date] = log
    
    # Check if today's mood is logged
    todays_mood = MoodLog.query.filter_by(
        student_id=student.id,
        log_date=date.today()
    ).first()
    
    return render_template('support_dashboard.html',
                         student=student,
                         todays_quote=todays_quote,
                         active_goals=active_goals,
                         mood_data=mood_data,
                         todays_mood=todays_mood,
                         ai_info=student_ai_info.get_student_comprehensive_info(student.id))

@support_bp.route('/goals')
@login_required
def goals():
    """Goals management page - STUDENT ONLY"""
    # STRICT: Only students can access this route
    if current_user.role != 'student':
        flash('Access denied. This area is for students only.', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Student profile not found. Please contact administrator.', 'danger')
        return redirect(url_for('main.login'))
    
    # Security check
    if student.user_id != current_user.id:
        flash('Access denied. Invalid student assignment.', 'danger')
        return redirect(url_for('main.login'))
    
    # Get all goals with different statuses
    active_goals = StudentGoal.query.filter_by(student_id=student.id, status='Active').order_by(StudentGoal.created_at.desc()).all()
    completed_goals = StudentGoal.query.filter_by(student_id=student.id, status='Completed').order_by(StudentGoal.updated_at.desc()).limit(10).all()
    abandoned_goals = StudentGoal.query.filter_by(student_id=student.id, status='Abandoned').order_by(StudentGoal.updated_at.desc()).limit(5).all()
    
    return render_template('goals.html',
                         student=student,
                         active_goals=active_goals,
                         completed_goals=completed_goals,
                         abandoned_goals=abandoned_goals)

@support_bp.route('/goals/add', methods=['POST'])
@login_required
def add_goal():
    """Add new goal"""
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    target_date_str = request.form.get('target_date', '').strip()
    
    if not title:
        flash('Goal title is required', 'danger')
        return redirect(url_for('support.goals'))
    
    try:
        target_date = None
        if target_date_str:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        
        goal = StudentGoal(
            student_id=student.id,
            title=title,
            description=description,
            target_date=target_date
        )
        
        db.session.add(goal)
        db.session.commit()
        
        flash('Goal added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding goal', 'danger')
    
    return redirect(url_for('support.goals'))

@support_bp.route('/goals/<int:goal_id>/update', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    """Update goal progress"""
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    goal = StudentGoal.query.get_or_404(goal_id)
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if goal.student_id != student.id:
        return jsonify({'error': 'Access denied'}), 403
    
    progress = request.form.get('progress', type=int)
    if progress is None or progress < 0 or progress > 100:
        return jsonify({'error': 'Invalid progress value'}), 400
    
    try:
        goal.progress = progress
        goal.updated_at = datetime.utcnow()
        
        # Auto-complete if progress reaches 100%
        if progress == 100:
            goal.status = 'Completed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress updated successfully',
            'status': goal.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update progress'}), 500

@support_bp.route('/goals/<int:goal_id>/complete', methods=['POST'])
@login_required
def complete_goal(goal_id):
    """Mark goal as completed"""
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    goal = StudentGoal.query.get_or_404(goal_id)
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if goal.student_id != student.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        goal.status = 'Completed'
        goal.progress = 100
        goal.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Goal marked as completed!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to complete goal'}), 500

@support_bp.route('/goals/<int:goal_id>/abandon', methods=['POST'])
@login_required
def abandon_goal(goal_id):
    """Abandon goal"""
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    goal = StudentGoal.query.get_or_404(goal_id)
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if goal.student_id != student.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        goal.status = 'Abandoned'
        goal.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Goal abandoned'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to abandon goal'}), 500

@support_bp.route('/mood', methods=['GET', 'POST'])
@login_required
def mood():
    """Mood tracking page"""
    if current_user.role != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Student profile not found', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        mood_score = request.form.get('mood_score', type=int)
        note = request.form.get('note', '').strip()
        
        if mood_score is None or mood_score < 1 or mood_score > 5:
            flash('Invalid mood score', 'danger')
            return redirect(url_for('support.mood'))
        
        try:
            # Check if mood already logged today
            todays_mood = MoodLog.query.filter_by(
                student_id=student.id,
                log_date=date.today()
            ).first()
            
            if todays_mood:
                # Update existing mood
                todays_mood.mood_score = mood_score
                todays_mood.note = note
                todays_mood.logged_at = datetime.utcnow()
            else:
                # Create new mood entry
                mood_log = MoodLog(
                    student_id=student.id,
                    mood_score=mood_score,
                    note=note
                )
                db.session.add(mood_log)
            
            db.session.commit()
            flash('Mood logged successfully!', 'success')
            return redirect(url_for('support.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error logging mood', 'danger')
    
    # Get mood history for last 30 days
    thirty_days_ago = date.today() - timedelta(days=30)
    mood_history = MoodLog.query.filter(
        MoodLog.student_id == student.id,
        MoodLog.log_date >= thirty_days_ago
    ).order_by(MoodLog.log_date.desc()).all()
    
    # Calculate mood statistics
    mood_stats = {}
    for score in range(1, 6):
        count = MoodLog.query.filter(
            MoodLog.student_id == student.id,
            MoodLog.mood_score == score,
            MoodLog.log_date >= thirty_days_ago
        ).count()
        mood_stats[score] = count
    
    return render_template('mood.html',
                         student=student,
                         mood_history=mood_history,
                         mood_stats=mood_stats)

@support_bp.route('/api/mood_log', methods=['POST'])
@login_required
def log_mood_api():
    """API endpoint for logging mood"""
    if current_user.role != 'student':
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    mood_score = request.json.get('mood_score')
    note = request.json.get('note', '')
    
    if mood_score is None or mood_score < 1 or mood_score > 5:
        return jsonify({'error': 'Invalid mood score'}), 400
    
    try:
        # Check if mood already logged today
        todays_mood = MoodLog.query.filter_by(
            student_id=student.id,
            log_date=date.today()
        ).first()
        
        if todays_mood:
            todays_mood.mood_score = mood_score
            todays_mood.note = note
            todays_mood.logged_at = datetime.utcnow()
        else:
            mood_log = MoodLog(
                student_id=student.id,
                mood_score=mood_score,
                note=note
            )
            db.session.add(mood_log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mood logged successfully',
            'mood_score': mood_score,
            'emoji': mood_log.get_mood_emoji() if 'mood_log' in locals() else todays_mood.get_mood_emoji()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to log mood'}), 500
