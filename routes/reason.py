"""
Reason Analysis Routes for EduGuard System
Handles student dropout reason analysis and reporting
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db, Student, StudentReason, User
from sqlalchemy import func

reason_bp = Blueprint('reason', __name__)

@reason_bp.route('/reason/analysis')
@login_required
def reason_analysis():
    """Reason analysis dashboard with pie charts"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        # Get reason statistics
        total_reasons = StudentReason.query.count()
        active_reasons = StudentReason.query.filter_by(status='Active').count()
        resolved_reasons = StudentReason.query.filter_by(status='Resolved').count()
        
        # Get reason category counts
        financial_count = StudentReason.query.filter(
            StudentReason.financial_reason.isnot(None),
            StudentReason.financial_reason != ''
        ).count()
        
        academic_count = StudentReason.query.filter(
            StudentReason.academic_reason.isnot(None),
            StudentReason.academic_reason != ''
        ).count()
        
        family_count = StudentReason.query.filter(
            StudentReason.family_reason.isnot(None),
            StudentReason.family_reason != ''
        ).count()
        
        health_count = StudentReason.query.filter(
            StudentReason.health_reason.isnot(None),
            StudentReason.health_reason != ''
        ).count()
        
        personal_count = StudentReason.query.filter(
            StudentReason.personal_reason.isnot(None),
            StudentReason.personal_reason != ''
        ).count()
        
        other_count = StudentReason.query.filter(
            StudentReason.other_reason.isnot(None),
            StudentReason.other_reason != ''
        ).count()
        
        # Get severity distribution
        severity_stats = db.session.query(
            StudentReason.severity,
            func.count(StudentReason.id).label('count')
        ).group_by(StudentReason.severity).all()
        
        # Get recent reasons
        recent_reasons = db.session.query(
            StudentReason, Student
        ).join(
            Student, StudentReason.student_id == Student.id
        ).order_by(StudentReason.created_at.desc()).limit(10).all()
        
        return render_template('reason/analysis.html',
                               total_reasons=total_reasons,
                               active_reasons=active_reasons,
                               resolved_reasons=resolved_reasons,
                               financial_count=financial_count,
                               academic_count=academic_count,
                               family_count=family_count,
                               health_count=health_count,
                               personal_count=personal_count,
                               other_count=other_count,
                               severity_stats=severity_stats,
                               recent_reasons=recent_reasons)
    except Exception as e:
        flash(f'Error loading reason analysis: {str(e)}', 'danger')
        return render_template('reason/analysis.html')

@reason_bp.route('/reason/submit', methods=['GET', 'POST'])
@login_required
def submit_reason():
    """Submit dropout reason form"""
    if current_user.role != 'student':
        abort(403)
    
    if request.method == 'POST':
        try:
            financial_reason = request.form.get('financial_reason')
            academic_reason = request.form.get('academic_reason')
            family_reason = request.form.get('family_reason')
            health_reason = request.form.get('health_reason')
            personal_reason = request.form.get('personal_reason')
            other_reason = request.form.get('other_reason')
            severity = request.form.get('severity')
            
            # Validate at least one reason is provided
            if not any([financial_reason, academic_reason, family_reason, health_reason, personal_reason, other_reason]):
                flash('Please provide at least one reason for dropout consideration', 'warning')
                return redirect(url_for('reason.submit_reason'))
            
            # Create reason record
            reason = StudentReason(
                student_id=current_user.student_profile.id,
                financial_reason=financial_reason,
                academic_reason=academic_reason,
                family_reason=family_reason,
                health_reason=health_reason,
                personal_reason=personal_reason,
                other_reason=other_reason,
                severity=severity
            )
            
            db.session.add(reason)
            db.session.commit()
            
            flash('Reason submitted successfully. Thank you for your feedback.', 'success')
            return redirect(url_for('reason.submit_reason'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting reason: {str(e)}', 'danger')
    
    return render_template('reason/submit.html')

@reason_bp.route('/reason/manage')
@login_required
def manage_reasons():
    """Manage student reasons (Admin/Faculty)"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        # Get all reasons with filtering
        page = request.args.get('page', 1, type=int)
        per_page = 20
        status_filter = request.args.get('status', 'All')
        severity_filter = request.args.get('severity', 'All')
        
        query = StudentReason.query.join(Student)
        
        # Apply filters
        if status_filter != 'All':
            query = query.filter(StudentReason.status == status_filter)
        
        if severity_filter != 'All':
            query = query.filter(StudentReason.severity == severity_filter)
        
        # Paginate
        reasons = query.order_by(StudentReason.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('reason/manage.html',
                               reasons=reasons,
                               status_filter=status_filter,
                               severity_filter=severity_filter)
    except Exception as e:
        flash(f'Error loading reasons: {str(e)}', 'danger')
        return render_template('reason/manage.html')

@reason_bp.route('/reason/<int:reason_id>/resolve', methods=['POST'])
@login_required
def resolve_reason(reason_id):
    """Mark a reason as resolved"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        reason = StudentReason.query.get_or_404(reason_id)
        reason.status = 'Resolved'
        reason.resolved_at = datetime.utcnow()
        reason.resolved_by = current_user.id
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Reason marked as resolved'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@reason_bp.route('/reason/api/statistics')
@login_required
def api_reason_statistics():
    """API endpoint for reason statistics"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        # Get comprehensive statistics
        stats = db.session.query(
            StudentReason.severity,
            func.count(StudentReason.id).label('count')
        ).group_by(StudentReason.severity).all()
        
        # Get category statistics
        category_stats = {
            'financial': StudentReason.query.filter(StudentReason.financial_reason.isnot(None), StudentReason.financial_reason != '').count(),
            'academic': StudentReason.query.filter(StudentReason.academic_reason.isnot(None), StudentReason.academic_reason != '').count(),
            'family': StudentReason.query.filter(StudentReason.family_reason.isnot(None), StudentReason.family_reason != '').count(),
            'health': StudentReason.query.filter(StudentReason.health_reason.isnot(None), StudentReason.health_reason != '').count(),
            'personal': StudentReason.query.filter(StudentReason.personal_reason.isnot(None), StudentReason.personal_reason != '').count(),
            'other': StudentReason.query.filter(StudentReason.other_reason.isnot(None), StudentReason.other_reason != '').count()
        }
        
        return jsonify({
            'severity_stats': dict([(s.severity, s.count) for s in stats]),
            'category_stats': category_stats,
            'total_reasons': StudentReason.query.count()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@reason_bp.route('/reason/api/trends')
@login_required
def api_reason_trends():
    """API endpoint for reason trends over time"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        # Get monthly trends
        monthly_trends = db.session.query(
            func.extract('year', StudentReason.created_at).label('year'),
            func.extract('month', StudentReason.created_at).label('month'),
            func.count(StudentReason.id).label('count')
        ).group_by(
            func.extract('year', StudentReason.created_at),
            func.extract('month', StudentReason.created_at)
        ).order_by(
            func.extract('year', StudentReason.created_at),
            func.extract('month', StudentReason.created_at)
        ).all()
        
        return jsonify({'trends': monthly_trends})
        
    except Exception as e:
        return jsonify({'error': str(e)})

# Helper functions
def get_reason_summary():
    """Get summary of all reasons"""
    try:
        reasons = StudentReason.query.all()
        
        summary = {
            'total': len(reasons),
            'by_category': {
                'financial': len([r for r in reasons if r.financial_reason]),
                'academic': len([r for r in reasons if r.academic_reason]),
                'family': len([r for r in reasons if r.family_reason]),
                'health': len([r for r in reasons if r.health_reason]),
                'personal': len([r for r in reasons if r.personal_reason]),
                'other': len([r for r in reasons if r.other_reason])
            },
            'by_severity': {
                'Critical': len([r for r in reasons if r.severity == 'Critical']),
                'High': len([r for r in reasons if r.severity == 'High']),
                'Medium': len([r for r in reasons if r.severity == 'Medium']),
                'Low': len([r for r in reasons if r.severity == 'Low'])
            }
        }
        
        return summary
        
    except Exception as e:
        return {'total': 0, 'by_category': {}, 'by_severity': {}}
