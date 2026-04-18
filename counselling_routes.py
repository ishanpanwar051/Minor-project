"""
Counselling System Routes
Complete counselling request management and scheduling
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models_enhanced import db, CounsellingRequest, Student, User, CounsellingStatus
from datetime import datetime, timedelta
from rbac_system import admin_required, student_required, get_student_for_current_user
import json

counselling_bp = Blueprint('counselling', __name__, url_prefix='/counselling')

# ================================
# Counselling System (Student)
# ================================

@counselling_bp.route('/')
@login_required
@student_required
def student_portal():
    """Student counselling portal"""
    student = get_student_for_current_user()
    if not student:
        return redirect(url_for('auth.login'))
    
    # Get student's counselling requests
    my_requests = CounsellingRequest.query.filter_by(student_id=student.id).order_by(
        CounsellingRequest.request_date.desc()
    ).all()
    
    return render_template('counselling/student_portal.html', 
                         student=student,
                         requests=my_requests)

@counselling_bp.route('/request', methods=['GET', 'POST'])
@login_required
@student_required
def create_request():
    """Create new counselling request"""
    student = get_student_for_current_user()
    if not student:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            counselling_request = CounsellingRequest(
                student_id=student.id,
                user_id=current_user.id,
                counselling_type=request.form.get('counselling_type'),
                topic=request.form.get('topic'),
                description=request.form.get('description'),
                priority=request.form.get('priority', 'medium'),
                preferred_date=datetime.strptime(request.form.get('preferred_date'), '%Y-%m-%d') if request.form.get('preferred_date') else None,
                preferred_time=request.form.get('preferred_time'),
                duration_minutes=int(request.form.get('duration_minutes', 60))
            )
            
            # AI Analysis
            counselling_request.ai_sentiment_score = analyze_sentiment(request.form.get('description', ''))
            counselling_request.ai_urgency_score = calculate_urgency_score(request.form.get('description', ''), request.form.get('priority', 'medium'))
            counselling_request.ai_topic_classification = classify_topic(request.form.get('topic', ''), request.form.get('counselling_type', ''))
            counselling_request.ai_recommended_actions = generate_recommendations(request.form.get('description', ''), request.form.get('counselling_type', ''))
            
            db.session.add(counselling_request)
            db.session.commit()
            
            # Send notification to admin
            from models_enhanced import Notification
            notification = Notification(
                user_id=User.query.filter_by(role='admin').first().id,
                title=f'New Counselling Request: {counselling_request.topic}',
                message=f'Student {student.first_name} {student.last_name} has requested counselling for {counselling_request.topic}',
                notification_type='counselling',
                action_required=True,
                action_url=url_for('counselling.admin_manage')
            )
            db.session.add(notification)
            db.session.commit()
            
            flash('Counselling request submitted successfully!', 'success')
            return redirect(url_for('counselling.student_portal'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting request: {str(e)}', 'danger')
    
    return render_template('counselling/create_request.html', student=student)

@counselling_bp.route('/request/<int:request_id>/edit', methods=['GET', 'POST'])
@login_required
@student_required
def edit_request(request_id):
    """Edit counselling request (only if not scheduled)"""
    student = get_student_for_current_user()
    if not student:
        return redirect(url_for('auth.login'))
    
    counselling_request = CounsellingRequest.query.get_or_404(request_id)
    
    # Verify ownership
    if counselling_request.student_id != student.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('counselling.student_portal'))
    
    # Can only edit if not scheduled
    if counselling_request.status != CounsellingStatus.REQUESTED:
        flash('Cannot edit request that has been scheduled', 'warning')
        return redirect(url_for('counselling.student_portal'))
    
    if request.method == 'POST':
        try:
            counselling_request.topic = request.form.get('topic')
            counselling_request.description = request.form.get('description')
            counselling_request.priority = request.form.get('priority', 'medium')
            counselling_request.preferred_date = datetime.strptime(request.form.get('preferred_date'), '%Y-%m-%d') if request.form.get('preferred_date') else None
            counselling_request.preferred_time = request.form.get('preferred_time')
            counselling_request.duration_minutes = int(request.form.get('duration_minutes', 60))
            
            # Update AI analysis
            counselling_request.ai_sentiment_score = analyze_sentiment(request.form.get('description', ''))
            counselling_request.ai_urgency_score = calculate_urgency_score(request.form.get('description', ''), request.form.get('priority', 'medium'))
            counselling_request.ai_topic_classification = classify_topic(request.form.get('topic', ''), request.form.get('counselling_type', ''))
            counselling_request.ai_recommended_actions = generate_recommendations(request.form.get('description', ''), request.form.get('counselling_type', ''))
            
            db.session.commit()
            flash('Request updated successfully!', 'success')
            return redirect(url_for('counselling.student_portal'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating request: {str(e)}', 'danger')
    
    return render_template('counselling/edit_request.html', request=counselling_request, student=student)

@counselling_bp.route('/request/<int:request_id>/cancel', methods=['POST'])
@login_required
@student_required
def cancel_request(request_id):
    """Cancel counselling request"""
    student = get_student_for_current_user()
    if not student:
        return redirect(url_for('auth.login'))
    
    counselling_request = CounsellingRequest.query.get_or_404(request_id)
    
    # Verify ownership
    if counselling_request.student_id != student.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('counselling.student_portal'))
    
    # Can only cancel if not completed
    if counselling_request.status == CounsellingStatus.COMPLETED:
        flash('Cannot cancel completed session', 'warning')
        return redirect(url_for('counselling.student_portal'))
    
    try:
        counselling_request.status = CounsellingStatus.CANCELLED
        db.session.commit()
        flash('Request cancelled successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling request: {str(e)}', 'danger')
    
    return redirect(url_for('counselling.student_portal'))

# ================================
# Counselling Management (Admin/Faculty)
# ================================

@counselling_bp.route('/admin')
@login_required
@admin_required
def admin_manage():
    """Admin counselling management dashboard"""
    
    # Get statistics
    total_requests = CounsellingRequest.query.count()
    pending_requests = CounsellingRequest.query.filter_by(status=CounsellingStatus.REQUESTED).count()
    scheduled_requests = CounsellingRequest.query.filter_by(status=CounsellingStatus.SCHEDULED).count()
    completed_requests = CounsellingRequest.query.filter_by(status=CounsellingStatus.COMPLETED).count()
    
    # Get recent requests
    recent_requests = CounsellingRequest.query.order_by(CounsellingRequest.request_date.desc()).limit(10).all()
    
    # Get urgent requests
    urgent_requests = CounsellingRequest.query.filter_by(priority='urgent').filter(
        CounsellingRequest.status.in_([CounsellingStatus.REQUESTED, CounsellingStatus.SCHEDULED])
    ).all()
    
    # Get counsellors
    counsellors = User.query.filter(User.role.in_(['admin', 'faculty'])).all()
    
    return render_template('counselling/admin_manage.html',
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         scheduled_requests=scheduled_requests,
                         completed_requests=completed_requests,
                         recent_requests=recent_requests,
                         urgent_requests=urgent_requests,
                         counsellors=counsellors)

@counselling_bp.route('/admin/requests')
@login_required
@admin_required
def admin_requests():
    """View all counselling requests"""
    
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    type_filter = request.args.get('type', 'all')
    
    query = CounsellingRequest.query.join(Student).join(User)
    
    if status_filter != 'all':
        query = query.filter(CounsellingRequest.status == CounsellingStatus[status_filter.upper()])
    
    if priority_filter != 'all':
        query = query.filter(CounsellingRequest.priority == priority_filter)
    
    if type_filter != 'all':
        query = query.filter(CounsellingRequest.counselling_type == type_filter)
    
    requests = query.order_by(CounsellingRequest.request_date.desc()).all()
    
    return render_template('counselling/admin_requests.html',
                         requests=requests,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         type_filter=type_filter)

@counselling_bp.route('/admin/request/<int:request_id>/schedule', methods=['GET', 'POST'])
@login_required
@admin_required
def schedule_request(request_id):
    """Schedule counselling request"""
    counselling_request = CounsellingRequest.query.get_or_404(request_id)
    
    if request.method == 'POST':
        try:
            counselling_request.status = CounsellingStatus.SCHEDULED
            counselling_request.assigned_counsellor_id = int(request.form.get('assigned_counsellor'))
            counselling_request.assigned_date = datetime.utcnow()
            counselling_request.scheduled_date = datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%d')
            counselling_request.scheduled_date = counselling_request.scheduled_date.replace(
                hour=int(request.form.get('scheduled_time').split(':')[0]),
                minute=int(request.form.get('scheduled_time').split(':')[1])
            )
            counselling_request.duration_minutes = int(request.form.get('duration_minutes', 60))
            
            db.session.commit()
            
            # Send notification to student
            from models_enhanced import Notification
            notification = Notification(
                user_id=counselling_request.student.user_id,
                title='Counselling Session Scheduled',
                message=f'Your counselling session for "{counselling_request.topic}" has been scheduled for {counselling_request.scheduled_date.strftime("%B %d, %Y at %I:%M %p")}',
                notification_type='counselling',
                action_url=url_for('counselling.student_portal')
            )
            db.session.add(notification)
            db.session.commit()
            
            flash('Session scheduled successfully!', 'success')
            return redirect(url_for('counselling.admin_requests'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error scheduling session: {str(e)}', 'danger')
    
    # Get available counsellors
    counsellors = User.query.filter(User.role.in_(['admin', 'faculty'])).all()
    
    return render_template('counselling/schedule.html', 
                         request=counselling_request,
                         counsellors=counsellors)

@counselling_bp.route('/admin/request/<int:request_id>/complete', methods=['GET', 'POST'])
@login_required
@admin_required
def complete_request(request_id):
    """Complete counselling session"""
    counselling_request = CounsellingRequest.query.get_or_404(request_id)
    
    if request.method == 'POST':
        try:
            counselling_request.status = CounsellingStatus.COMPLETED
            counselling_request.session_notes = request.form.get('session_notes')
            counselling_request.follow_up_required = 'follow_up_required' in request.form
            counselling_request.follow_up_date = datetime.strptime(request.form.get('follow_up_date'), '%Y-%m-%d') if request.form.get('follow_up_date') else None
            
            db.session.commit()
            
            # Send notification to student
            from models_enhanced import Notification
            notification = Notification(
                user_id=counselling_request.student.user_id,
                title='Counselling Session Completed',
                message=f'Your counselling session for "{counselling_request.topic}" has been marked as completed',
                notification_type='counselling',
                action_url=url_for('counselling.student_portal')
            )
            db.session.add(notification)
            db.session.commit()
            
            flash('Session completed successfully!', 'success')
            return redirect(url_for('counselling.admin_requests'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error completing session: {str(e)}', 'danger')
    
    return render_template('counselling/complete.html', request=counselling_request)

@counselling_bp.route('/admin/request/<int:request_id>/details')
@login_required
@admin_required
def request_details(request_id):
    """View detailed counselling request"""
    counselling_request = CounsellingRequest.query.get_or_404(request_id)
    
    return render_template('counselling/details.html', request=counselling_request)

# ================================
# API Endpoints
# ================================

@counselling_bp.route('/api/request/<int:request_id>/status')
@login_required
def api_request_status(request_id):
    """API endpoint to get request status"""
    
    counselling_request = CounsellingRequest.query.get_or_404(request_id)
    
    # Verify access (student can only see own requests)
    if current_user.role == 'student':
        student = get_student_for_current_user()
        if not student or counselling_request.student_id != student.id:
            return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': counselling_request.id,
        'status': counselling_request.status.value,
        'topic': counselling_request.topic,
        'scheduled_date': counselling_request.scheduled_date.isoformat() if counselling_request.scheduled_date else None,
        'assigned_counsellor': counselling_request.assigned_counsellor.username if counselling_request.assigned_counsellor else None,
        'session_notes': counselling_request.session_notes,
        'follow_up_required': counselling_request.follow_up_required,
        'follow_up_date': counselling_request.follow_up_date.isoformat() if counselling_request.follow_up_date else None
    })

@counselling_bp.route('/api/analytics')
@login_required
@admin_required
def api_analytics():
    """API endpoint for counselling analytics"""
    
    # Request trends (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_requests = CounsellingRequest.query.filter(
        CounsellingRequest.request_date >= thirty_days_ago
    ).count()
    
    # Status distribution
    status_distribution = db.session.query(
        CounsellingRequest.status,
        func.count(CounsellingRequest.id).label('count')
    ).group_by(CounsellingRequest.status).all()
    
    # Type distribution
    type_distribution = db.session.query(
        CounsellingRequest.counselling_type,
        func.count(CounsellingRequest.id).label('count')
    ).group_by(CounsellingRequest.counselling_type).all()
    
    # Priority distribution
    priority_distribution = db.session.query(
        CounsellingRequest.priority,
        func.count(CounsellingRequest.id).label('count')
    ).group_by(CounsellingRequest.priority).all()
    
    # Average session duration
    avg_duration = db.session.query(
        func.avg(CounsellingRequest.duration_minutes)
    ).filter(CounsellingRequest.status == CounsellingStatus.COMPLETED).scalar() or 0
    
    return jsonify({
        'recent_requests': recent_requests,
        'status_distribution': {status.value: count for status, count in status_distribution},
        'type_distribution': {type_: count for type_, count in type_distribution},
        'priority_distribution': {priority: count for priority, count in priority_distribution},
        'average_duration': avg_duration
    })

# ================================
# AI Helper Functions
# ================================

def analyze_sentiment(text):
    """Simple sentiment analysis (0-1 scale)"""
    
    positive_words = ['happy', 'good', 'great', 'excellent', 'wonderful', 'amazing', 'positive', 'excited', 'confident']
    negative_words = ['sad', 'bad', 'terrible', 'awful', 'worried', 'anxious', 'stressed', 'depressed', 'concerned', 'struggling']
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    total_words = len(text.split())
    
    if total_words == 0:
        return 0.5  # Neutral
    
    sentiment_score = (positive_count - negative_count) / total_words + 0.5
    return max(0, min(1, sentiment_score))

def calculate_urgency_score(description, priority):
    """Calculate urgency score (0-1 scale)"""
    
    urgency_keywords = ['urgent', 'emergency', 'immediate', 'critical', 'asap', 'soon', 'quickly']
    description_lower = description.lower()
    
    keyword_score = sum(1 for word in urgency_keywords if word in description_lower) * 0.2
    
    # Priority-based score
    priority_scores = {'low': 0.2, 'medium': 0.5, 'high': 0.8, 'urgent': 1.0}
    priority_score = priority_scores.get(priority, 0.5)
    
    # Length-based urgency (shorter descriptions might indicate more urgent issues)
    length_score = max(0, 1 - len(description) / 500) * 0.1
    
    urgency_score = priority_score + keyword_score + length_score
    return min(1, urgency_score)

def classify_topic(topic, counselling_type):
    """Classify topic for better categorization"""
    
    topic_lower = topic.lower()
    
    # Academic topics
    if any(word in topic_lower for word in ['study', 'grade', 'course', 'exam', 'academic', 'gpa']):
        return 'academic_support'
    
    # Career topics
    elif any(word in topic_lower for word in ['career', 'job', 'future', 'employment', 'internship']):
        return 'career_guidance'
    
    # Personal topics
    elif any(word in topic_lower for word in ['personal', 'family', 'relationship', 'social']):
        return 'personal_issues'
    
    # Financial topics
    elif any(word in topic_lower for word in ['financial', 'money', 'tuition', 'expense', 'budget']):
        return 'financial_concerns'
    
    # Mental health topics
    elif any(word in topic_lower for word in ['stress', 'anxiety', 'depression', 'mental', 'health']):
        return 'mental_health'
    
    else:
        return counselling_type or 'general'

def generate_recommendations(description, counselling_type):
    """Generate AI recommendations for counsellors"""
    
    recommendations = []
    
    description_lower = description.lower()
    
    # Academic recommendations
    if counselling_type == 'academic':
        recommendations.extend([
            'Review current academic performance and study habits',
            'Consider academic support services',
            'Explore time management strategies'
        ])
    
    # Career recommendations
    elif counselling_type == 'career':
        recommendations.extend([
            'Assess skills and interests',
            'Explore career resources and tools',
            'Consider internship opportunities'
        ])
    
    # Personal recommendations
    elif counselling_type == 'personal':
        recommendations.extend([
            'Provide supportive listening environment',
            'Discuss coping strategies',
            'Consider referral to specialized services if needed'
        ])
    
    # Financial recommendations
    elif counselling_type == 'financial':
        recommendations.extend([
            'Review financial aid options',
            'Discuss budgeting strategies',
            'Connect with financial aid office'
        ])
    
    # Based on content analysis
    if 'stress' in description_lower or 'anxiety' in description_lower:
        recommendations.append('Discuss stress management techniques')
    
    if 'family' in description_lower:
        recommendations.append('Consider family dynamics and support systems')
    
    if 'future' in description_lower or 'goal' in description_lower:
        recommendations.append('Focus on goal setting and planning')
    
    return '; '.join(recommendations) if recommendations else 'Provide general support and guidance'
