"""
Performance Tracker Routes for EduGuard System
Handles student performance improvement tracking with charts
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from models import db, Student, PerformanceTracker
import json

performance_bp = Blueprint('performance', __name__)

@performance_bp.route('/performance')
@login_required
def performance_dashboard():
    """Performance tracking dashboard"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        # Get performance statistics
        total_records = PerformanceTracker.query.count()
        students_with_improvement = db.session.query(
            db.func.count(db.func.distinct(PerformanceTracker.student_id))
        ).filter(PerformanceTracker.improvement_percentage > 0).scalar() or 0
        
        # Get average improvement
        avg_improvement = db.session.query(
            db.func.avg(PerformanceTracker.improvement_percentage)
        ).filter(PerformanceTracker.improvement_percentage > 0).scalar() or 0
        
        # Get subject-wise performance
        subject_performance = db.session.query(
            PerformanceTracker.subject_name,
            db.func.avg(PerformanceTracker.improvement_percentage).label('avg_improvement'),
            db.func.count(PerformanceTracker.id).label('record_count')
        ).group_by(PerformanceTracker.subject_name).all()
        
        # Get recent improvements
        recent_improvements = db.session.query(
            PerformanceTracker, Student
        ).join(
            Student, PerformanceTracker.student_id == Student.id
        ).filter(
            PerformanceTracker.improvement_percentage > 0
        ).order_by(PerformanceTracker.created_at.desc()).limit(10).all()
        
        return render_template('performance/dashboard.html',
                               total_records=total_records,
                               students_with_improvement=students_with_improvement,
                               avg_improvement=round(avg_improvement, 2),
                               subject_performance=subject_performance,
                               recent_improvements=recent_improvements)
    except Exception as e:
        flash(f'Error loading performance dashboard: {str(e)}', 'danger')
        return render_template('performance/dashboard.html')

@performance_bp.route('/performance/student/<int:student_id>')
@login_required
def student_performance(student_id):
    """View individual student performance with charts"""
    # Check permissions
    if current_user.role == 'student' and student_id != current_user.student_profile.id:
        abort(403)
    
    student = Student.query.get_or_404(student_id)
    
    try:
        # Get student's performance records
        performance_records = PerformanceTracker.query.filter_by(
            student_id=student_id
        ).order_by(PerformanceTracker.exam_date.desc()).all()
        
        # Calculate statistics
        total_exams = len(performance_records)
        improved_exams = len([p for p in performance_records if p.improvement_percentage > 0])
        avg_improvement = sum([p.improvement_percentage for p in performance_records]) / total_exams if total_exams > 0 else 0
        
        # Prepare chart data
        chart_data = []
        for record in performance_records:
            chart_data.append({
                'date': record.exam_date.strftime('%Y-%m-%d'),
                'before_score': record.before_score,
                'after_score': record.after_score,
                'improvement': record.improvement_percentage,
                'subject': record.subject_name,
                'exam_type': record.exam_type
            })
        
        return render_template('performance/student_detail.html',
                               student=student,
                               performance_records=performance_records,
                               chart_data=json.dumps(chart_data),
                               total_exams=total_exams,
                               improved_exams=improved_exams,
                               avg_improvement=round(avg_improvement, 2))
    except Exception as e:
        flash(f'Error loading student performance: {str(e)}', 'danger')
        return redirect(url_for('performance.performance_dashboard'))

@performance_bp.route('/performance/add', methods=['GET', 'POST'])
@login_required
def add_performance_record():
    """Add new performance record"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            subject_name = request.form.get('subject_name')
            exam_type = request.form.get('exam_type')
            before_score = float(request.form.get('before_score'))
            after_score = float(request.form.get('after_score'))
            max_score = float(request.form.get('max_score', 100))
            exam_date = datetime.strptime(request.form.get('exam_date'), '%Y-%m-%d').date()
            semester = int(request.form.get('semester'))
            notes = request.form.get('notes')
            
            # Create performance record
            performance = PerformanceTracker(
                student_id=student_id,
                subject_name=subject_name,
                exam_type=exam_type,
                before_score=before_score,
                after_score=after_score,
                max_score=max_score,
                exam_date=exam_date,
                semester=semester,
                notes=notes
            )
            
            # Calculate improvement
            performance.calculate_improvement()
            
            db.session.add(performance)
            db.session.commit()
            
            flash('Performance record added successfully!', 'success')
            return redirect(url_for('performance.performance_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding performance record: {str(e)}', 'danger')
    
    # Get students for dropdown
    students = Student.query.order_by(Student.last_name).all()
    return render_template('performance/add.html', students=students)

@performance_bp.route('/performance/api/chart_data/<int:student_id>')
@login_required
def get_chart_data(student_id):
    """API endpoint for performance chart data"""
    # Check permissions
    if current_user.role == 'student' and student_id != current_user.student_profile.id:
        abort(403)
    
    try:
        performance_records = PerformanceTracker.query.filter_by(
            student_id=student_id
        ).order_by(PerformanceTracker.exam_date.asc()).all()
        
        chart_data = {
            'labels': [],
            'before_scores': [],
            'after_scores': [],
            'improvements': []
        }
        
        for record in performance_records:
            chart_data['labels'].append(record.subject_name + ' - ' + record.exam_date.strftime('%b %d'))
            chart_data['before_scores'].append(record.before_score)
            chart_data['after_scores'].append(record.after_score)
            chart_data['improvements'].append(record.improvement_percentage)
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@performance_bp.route('/performance/api/subject_stats')
@login_required
def get_subject_stats():
    """API endpoint for subject-wise statistics"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    try:
        subject_stats = db.session.query(
            PerformanceTracker.subject_name,
            db.func.avg(PerformanceTracker.before_score).label('avg_before'),
            db.func.avg(PerformanceTracker.after_score).label('avg_after'),
            db.func.avg(PerformanceTracker.improvement_percentage).label('avg_improvement'),
            db.func.count(PerformanceTracker.id).label('record_count')
        ).group_by(PerformanceTracker.subject_name).all()
        
        stats_data = []
        for stat in subject_stats:
            stats_data.append({
                'subject': stat.subject_name,
                'avg_before': round(stat.avg_before or 0, 2),
                'avg_after': round(stat.avg_after or 0, 2),
                'avg_improvement': round(stat.avg_improvement or 0, 2),
                'record_count': stat.record_count
            })
        
        return jsonify({'data': stats_data})
        
    except Exception as e:
        return jsonify({'error': str(e)})

# Helper functions
def calculate_performance_trends(student_id):
    """Calculate performance trends for a student"""
    try:
        records = PerformanceTracker.query.filter_by(student_id=student_id).order_by(PerformanceTracker.exam_date.asc()).all()
        
        if len(records) < 2:
            return None
        
        # Calculate trend
        first_half = records[:len(records)//2]
        second_half = records[len(records)//2:]
        
        first_avg = sum([r.improvement_percentage for r in first_half]) / len(first_half)
        second_avg = sum([r.improvement_percentage for r in second_half]) / len(second_half)
        
        trend = 'improving' if second_avg > first_avg else 'declining' if second_avg < first_avg else 'stable'
        
        return {
            'trend': trend,
            'first_avg': round(first_avg, 2),
            'second_avg': round(second_avg, 2),
            'change': round(second_avg - first_avg, 2)
        }
    except Exception as e:
        return None
