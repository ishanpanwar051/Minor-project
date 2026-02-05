"""
Student Dashboard Routes for EduGuard System
Handles student personal dashboard with graphs and personalized tips
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import db, Student, Attendance, AcademicRecord, RiskProfile, PerformanceTracker
import json

student_bp = Blueprint('student', __name__)

@student_bp.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student personal dashboard"""
    if current_user.role != 'student':
        abort(403)
    
    try:
        # Get student profile
        student = current_user.student_profile
        
        if not student:
            flash('Student profile not found', 'warning')
            return redirect(url_for('main.dashboard'))
        
        # Get attendance data for charts
        attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).limit(30).all()
        attendance_rate = len([a for a in attendance_records if a.status == 'Present']) / len(attendance_records) * 100 if attendance_records else 0
        
        # Get academic records
        academic_records = AcademicRecord.query.filter_by(student_id=student.id).order_by(AcademicRecord.exam_date.desc()).limit(10).all()
        
        # Get performance improvements
        performance_records = PerformanceTracker.query.filter_by(student_id=student.id).order_by(PerformanceTracker.created_at.desc()).limit(5).all()
        
        # Get risk profile
        risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
        
        # Generate personalized tips
        tips = generate_personalized_tips(student, risk_profile, attendance_rate, academic_records)
        
        return render_template('student/dashboard.html',
                               student=student,
                               attendance_rate=attendance_rate,
                               attendance_records=attendance_records,
                               academic_records=academic_records,
                               performance_records=performance_records,
                               risk_profile=risk_profile,
                               tips=tips)
    except Exception as e:
        flash(f'Error loading student dashboard: {str(e)}', 'danger')
        return render_template('student/dashboard.html')

@student_bp.route('/student/profile')
@login_required
def student_profile():
    """Student profile management"""
    if current_user.role != 'student':
        abort(403)
    
    student = current_user.student_profile
    
    if request.method == 'POST':
        try:
            # Update student profile
            student.first_name = request.form.get('first_name')
            student.last_name = request.form.get('last_name')
            student.email = request.form.get('email')
            student.phone = request.form.get('phone')
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('student.student_profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
    
    return render_template('student/profile.html', student=student)

@student_bp.route('/student/attendance')
@login_required
def student_attendance():
    """Student attendance history and trends"""
    if current_user.role != 'student':
        abort(403)
    
    student = current_user.student_profile
    
    # Get attendance data
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('student/attendance.html', 
                           student=student,
                           attendance_records=attendance_records)

@student_bp.route('/student/grades')
@login_required
def student_grades():
    """Student academic records and performance"""
    if current_user.role != 'student':
        abort(403)
    
    student = current_user.student_profile
    
    # Get academic records
    academic_records = AcademicRecord.query.filter_by(student_id=student.id).order_by(AcademicRecord.exam_date.desc()).all()
    
    # Calculate statistics
    total_courses = len(academic_records)
    avg_grade_points = sum([ar.calculate_grade_points() for ar in academic_records]) / total_courses if total_courses > 0 else 0
    avg_percentage = sum([ar.percentage() for ar in academic_records]) / total_courses if total_courses > 0 else 0
    
    return render_template('student/grades.html',
                           student=student,
                           academic_records=academic_records,
                           total_courses=total_courses,
                           avg_grade_points=round(avg_grade_points, 2),
                           avg_percentage=round(avg_percentage, 2))

@student_bp.route('/student/api/attendance_data')
@login_required
def api_attendance_data():
    """API endpoint for attendance chart data"""
    if current_user.role != 'student':
        abort(403)
    
    student = current_user.student_profile
    
    try:
        # Get last 30 days of attendance
        thirty_days_ago = date.today() - timedelta(days=30)
        attendance_records = Attendance.query.filter(
            Attendance.student_id == student.id,
            Attendance.date >= thirty_days_ago
        ).order_by(Attendance.date.asc()).all()
        
        # Prepare data for chart
        chart_data = {
            'labels': [record.date.strftime('%Y-%m-%d') for record in attendance_records],
            'present': [1 if record.status == 'Present' else 0 for record in attendance_records],
            'absent': [1 if record.status == 'Absent' else 0 for record in attendance_records],
            'late': [1 if record.status == 'Late' else 0 for record in attendance_records],
            'excused': [1 if record.status == 'Excused' else 0 for record in attendance_records]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@student_bp.route('/student/api/grade_data')
@login_required
def api_grade_data():
    """API endpoint for grade chart data"""
    if current_user.role != 'student':
        abort(403)
    
    student = current_user.student_profile
    
    try:
        academic_records = AcademicRecord.query.filter_by(student_id=student.id).order_by(AcademicRecord.exam_date.asc()).all()
        
        chart_data = {
            'labels': [f"{record.course_code} - {record.exam_date.strftime('%b %d')}" for record in academic_records],
            'grades': [record.calculate_grade_points() * 25 for record in academic_records],
            'percentages': [record.percentage() for record in academic_records]
        }
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@student_bp.route('/student/api/risk_prediction')
@login_required
def api_risk_prediction():
    """API endpoint for current student's risk prediction"""
    if current_user.role != 'student':
        abort(403)
    
    student = current_user.student_profile
    risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
    
    if not risk_profile:
        return jsonify({'error': 'Risk profile not found'})
    
    return jsonify({
        'risk_score': risk_profile.risk_score,
        'risk_level': risk_profile.risk_level,
        'ml_prediction': risk_profile.ml_prediction,
        'ml_probability': risk_profile.ml_probability,
        'last_updated': risk_profile.last_updated.strftime('%Y-%m-%d') if risk_profile.last_updated else None,
        'factors': {
            'attendance_factor': risk_profile.attendance_factor,
            'academic_factor': risk_profile.academic_factor,
            'engagement_factor': risk_profile.engagement_factor,
            'demographic_factor': risk_profile.demographic_factor
        }
    })

# Helper functions
def generate_personalized_tips(student, risk_profile, attendance_rate, academic_records):
    """Generate personalized improvement tips for students"""
    tips = []
    
    # Attendance-based tips
    if attendance_rate < 70:
        tips.append({
            'icon': 'fa-calendar-check',
            'title': 'Improve Your Attendance',
            'description': 'Regular attendance is crucial for academic success. Try to maintain at least 80% attendance.',
            'priority': 'high'
        })
    
    # Academic performance tips
    if academic_records:
        avg_grade = sum([ar.calculate_grade_points() for ar in academic_records]) / len(academic_records)
        if avg_grade < 2.0:
            tips.append({
                'icon': 'fa-book',
                'title': 'Focus on Academic Performance',
                'description': 'Your current grades need improvement. Consider tutoring, study groups, and meeting with professors during office hours.',
                'priority': 'high'
            })
        elif avg_grade < 3.0:
            tips.append({
                'icon': 'fa-chart-line',
                'title': 'Maintain Good Grades',
                'description': 'You have good academic standing. Keep up the good work and aim for consistency.',
                'priority': 'medium'
            })
    
    # Risk-based tips
    if risk_profile:
        if risk_profile.risk_level in ['High', 'Critical']:
            tips.append({
                'icon': 'fa-exclamation-triangle',
                'title': 'Seek Support Immediately',
                'description': 'Your risk level requires immediate attention. Please contact your academic advisor or counselor for support.',
                'priority': 'critical'
            })
        elif risk_profile.risk_level == 'Medium':
            tips.append({
                'icon': 'fa-exclamation-circle',
                'title': 'Monitor Your Progress',
                'description': 'You have some risk factors. Stay focused on your studies and utilize available resources.',
                'priority': 'medium'
            })
    
    # General tips
    tips.append({
        'icon': 'fa-lightbulb',
        'title': 'Use University Resources',
        'description': 'Take advantage of tutoring services, study groups, and academic support programs available on campus.',
        'priority': 'low'
    })
    
    tips.append({
        'icon': 'fa-clock',
        'title': 'Time Management',
        'description': 'Create a balanced study schedule and stick to it for better academic performance.',
        'priority': 'low'
    })
    
    return sorted(tips, key=lambda x: x['priority'], reverse=True)

def calculate_attendance_trend(student_id, days=30):
    """Calculate attendance trend over specified days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    attendance_records = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).all()
    
    if not attendance_records:
        return 0
    
    present_days = len([a for a in attendance_records if a.status == 'Present'])
    total_days = len(attendance_records)
    
    return (present_days / total_days) * 100 if total_days > 0 else 0

def calculate_grade_trend(student_id):
    """Calculate grade trend over recent assessments"""
    academic_records = AcademicRecord.query.filter_by(student_id=student_id).order_by(AcademicRecord.exam_date.desc()).limit(10).all()
    
    if len(academic_records) < 2:
        return 0
    
    recent_grades = [ar.calculate_grade_points() for ar in academic_records[:5]]
    older_grades = [ar.calculate_grade_points() for ar in academic_records[5:]]
    
    recent_avg = sum(recent_grades) / len(recent_grades)
    older_avg = sum(older_grades) / len(older_grades)
    
    return ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
