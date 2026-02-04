"""
Fixed Main Routes for EduGuard System
Handles dashboard, students, analytics, and student profiles with proper error handling
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from models import db, User, Student, Attendance, AcademicRecord, Intervention, RiskProfile, Alert
from datetime import datetime, date, timedelta
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redirect to login or dashboard based on auth status"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with comprehensive statistics"""
    try:
        # Get basic statistics
        total_students = Student.query.count()
        
        # Get risk level counts
        high_risk_count = RiskProfile.query.filter_by(risk_level='High').count()
        medium_risk_count = RiskProfile.query.filter_by(risk_level='Medium').count()
        low_risk_count = RiskProfile.query.filter_by(risk_level='Low').count()
        critical_risk_count = RiskProfile.query.filter_by(risk_level='Critical').count()
        
        # Get recent interventions
        recent_interventions = Intervention.query.order_by(Intervention.date.desc()).limit(5).all()
        
        # Get recent alerts
        recent_alerts = Alert.query.filter_by(status='Active').order_by(Alert.created_at.desc()).limit(5).all()
        
        # Get attendance statistics
        attendance_stats = get_attendance_stats()
        
        # Get academic performance stats
        academic_stats = get_academic_stats()
        
        return render_template('dashboard_college.html', 
                               total_students=total_students,
                               high_risk_count=high_risk_count + critical_risk_count,
                               medium_risk_count=medium_risk_count,
                               low_risk_count=low_risk_count,
                               critical_risk_count=critical_risk_count,
                               recent_interventions=recent_interventions,
                               recent_alerts=recent_alerts,
                               attendance_stats=attendance_stats,
                               academic_stats=academic_stats)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('dashboard_college.html', 
                               total_students=0,
                               high_risk_count=0,
                               medium_risk_count=0,
                               low_risk_count=0,
                               critical_risk_count=0,
                               recent_interventions=[],
                               recent_alerts=[],
                               attendance_stats={},
                               academic_stats={})

@main_bp.route('/students')
@login_required
def students():
    """Students listing with filtering and search"""
    if current_user.role == 'student':
        abort(403)
    
    try:
        # Get query parameters
        search = request.args.get('search', '')
        risk_level = request.args.get('risk_level', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build query
        query = Student.query
        
        # Apply search filter
        if search:
            query = query.filter(
                (Student.first_name.ilike(f'%{search}%')) |
                (Student.last_name.ilike(f'%{search}%')) |
                (Student.student_id.ilike(f'%{search}%')) |
                (Student.email.ilike(f'%{search}%'))
            )
        
        # Apply risk level filter
        if risk_level:
            query = query.join(RiskProfile).filter(RiskProfile.risk_level == risk_level)
        
        # Paginate results
        students = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('students.html', 
                               students=students,
                               search=search,
                               risk_level=risk_level)
    except Exception as e:
        flash(f'Error loading students: {str(e)}', 'danger')
        return render_template('students.html', students=None)

@main_bp.route('/student/<int:id>')
@login_required
def student_detail(id):
    """Detailed student profile"""
    try:
        # Get student
        student = Student.query.get_or_404(id)
        
        # Check permissions
        if current_user.role == 'student' and current_user.student_profile.id != id:
            abort(403)
        
        # Get student data
        attendance_records = Attendance.query.filter_by(student_id=id).order_by(Attendance.date.desc()).limit(30).all()
        academic_records = AcademicRecord.query.filter_by(student_id=id).order_by(AcademicRecord.exam_date.desc()).all()
        interventions = Intervention.query.filter_by(student_id=id).order_by(Intervention.date.desc()).all()
        risk_profile = RiskProfile.query.filter_by(student_id=id).first()
        alerts = Alert.query.filter_by(student_id=id).order_by(Alert.created_at.desc()).limit(10).all()
        
        # Calculate statistics
        attendance_rate = calculate_attendance_rate(attendance_records)
        average_score = calculate_average_score(academic_records)
        
        return render_template('student_detail.html', 
                               student=student,
                               risk=risk_profile,
                               attendance=attendance_records,
                               grades=academic_records,
                               interventions=interventions,
                               alerts=alerts,
                               attendance_rate=attendance_rate,
                               average_score=average_score)
    except Exception as e:
        flash(f'Error loading student details: {str(e)}', 'danger')
        return redirect(url_for('main.students'))

@main_bp.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard with charts and insights"""
    if current_user.role == 'student':
        abort(403)
    
    try:
        # Get risk distribution
        risk_counts = {
            'Critical': RiskProfile.query.filter_by(risk_level='Critical').count(),
            'High': RiskProfile.query.filter_by(risk_level='High').count(),
            'Medium': RiskProfile.query.filter_by(risk_level='Medium').count(),
            'Low': RiskProfile.query.filter_by(risk_level='Low').count()
        }
        
        # Get attendance trends
        attendance_trends = get_attendance_trends()
        
        # Get academic performance trends
        academic_trends = get_academic_trends()
        
        # Get intervention effectiveness
        intervention_stats = get_intervention_stats()
        
        return render_template('analytics.html', 
                               risk_counts=risk_counts,
                               attendance_trends=attendance_trends,
                               academic_trends=academic_trends,
                               intervention_stats=intervention_stats)
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'danger')
        return render_template('analytics.html', risk_counts={})

@main_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """AI prediction page for dropout risk"""
    if current_user.role not in ['admin', 'faculty']:
        abort(403)
    
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            
            if not student_id:
                flash('Please select a student', 'danger')
                return redirect(url_for('main.predict'))
            
            student = Student.query.filter_by(student_id=student_id).first()
            if not student:
                flash('Student not found', 'danger')
                return redirect(url_for('main.predict'))
            
            # Calculate risk prediction
            prediction = calculate_risk_prediction(student)
            
            return render_template('prediction_result.html', 
                                   student=student,
                                   prediction=prediction)
        except Exception as e:
            flash(f'Error calculating prediction: {str(e)}', 'danger')
    
    # Get all students for dropdown
    students = Student.query.all()
    return render_template('predict.html', students=students)

@main_bp.route('/api/student_risk_data/<int:student_id>')
@login_required
def api_student_risk_data(student_id):
    """API endpoint for student risk data (for charts)"""
    try:
        student = Student.query.get_or_404(student_id)
        
        # Get historical data
        attendance_data = get_historical_attendance(student_id)
        academic_data = get_historical_academic(student_id)
        
        return jsonify({
            'attendance': attendance_data,
            'academic': academic_data,
            'current_risk': student.risk_profile.risk_score if student.risk_profile else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper functions
def get_attendance_stats():
    """Calculate overall attendance statistics"""
    try:
        total_records = Attendance.query.count()
        present_records = Attendance.query.filter_by(status='Present').count()
        
        if total_records > 0:
            attendance_rate = (present_records / total_records) * 100
        else:
            attendance_rate = 0
        
        return {
            'total_classes': total_records,
            'present_classes': present_records,
            'attendance_rate': round(attendance_rate, 2)
        }
    except:
        return {'total_classes': 0, 'present_classes': 0, 'attendance_rate': 0}

def get_academic_stats():
    """Calculate college academic statistics"""
    try:
        academic_records = AcademicRecord.query.all()
        students = Student.query.all()
        
        if academic_records and students:
            # Calculate average GPA
            total_gpa = sum([student.gpa for student in students])
            average_gpa = total_gpa / len(students)
            
            # Count failing courses (grades below C)
            failing_courses = len([ar for ar in academic_records if ar.grade in ['D+', 'D', 'F']])
            
            # Count students on academic probation (GPA < 2.0)
            probation_students = len([s for s in students if s.gpa < 2.0])
        else:
            average_gpa = 0
            failing_courses = 0
            probation_students = 0
        
        return {
            'average_gpa': round(average_gpa, 2),
            'failing_courses': failing_courses,
            'probation_students': probation_students,
            'total_records': len(academic_records)
        }
    except:
        return {'average_gpa': 0, 'failing_courses': 0, 'probation_students': 0, 'total_records': 0}

def calculate_attendance_rate(attendance_records):
    """Calculate attendance rate for a student"""
    if not attendance_records:
        return 0
    
    present_count = len([a for a in attendance_records if a.status == 'Present'])
    return round((present_count / len(attendance_records)) * 100, 2)

def calculate_average_score(academic_records):
    """Calculate average score for a student"""
    if not academic_records:
        return 0
    
    total_percentage = sum([ar.percentage() for ar in academic_records])
    return round(total_percentage / len(academic_records), 2)

def get_attendance_trends():
    """Get attendance trends over time"""
    # This would typically query attendance data over time
    # For now, return mock data
    return {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'data': [85, 87, 83, 89, 91, 88]
    }

def get_academic_trends():
    """Get academic performance trends"""
    # This would typically query academic data over time
    # For now, return mock data
    return {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'data': [75, 78, 72, 80, 82, 79]
    }

def get_intervention_stats():
    """Get intervention effectiveness statistics"""
    try:
        total_interventions = Intervention.query.count()
        resolved_interventions = Intervention.query.filter_by(status='Resolved').count()
        
        if total_interventions > 0:
            success_rate = (resolved_interventions / total_interventions) * 100
        else:
            success_rate = 0
        
        return {
            'total': total_interventions,
            'resolved': resolved_interventions,
            'success_rate': round(success_rate, 2)
        }
    except:
        return {'total': 0, 'resolved': 0, 'success_rate': 0}

def calculate_risk_prediction(student):
    """Calculate AI-based risk prediction for a college student"""
    try:
        # Get student data
        attendance_records = Attendance.query.filter_by(student_id=student.id).all()
        academic_records = AcademicRecord.query.filter_by(student_id=student.id).all()
        interventions = Intervention.query.filter_by(student_id=student.id).all()
        
        # Calculate college-specific factors
        attendance_rate = calculate_attendance_rate(attendance_records)
        gpa = student.gpa or 0.0
        intervention_count = len(interventions)
        
        # Count failing courses
        failing_courses = len([ar for ar in academic_records if ar.grade in ['D+', 'D', 'F']])
        
        # Check academic probation status
        on_probation = gpa < 2.0
        
        # Risk calculation for college students
        gpa_risk = max(0, (4.0 - gpa) * 25)  # GPA is primary factor
        attendance_risk = max(0, (100 - attendance_rate) * 0.3)  # 30% weight
        academic_risk = min(30, failing_courses * 8)  # Failing courses risk
        intervention_risk = min(20, intervention_count * 4)  # Intervention history
        probation_risk = 25 if on_probation else 0  # Probation penalty
        
        total_risk = gpa_risk + attendance_risk + academic_risk + intervention_risk + probation_risk
        
        # Determine risk level
        if total_risk >= 80:
            risk_level = 'Critical'
        elif total_risk >= 60:
            risk_level = 'High'
        elif total_risk >= 40:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        return {
            'risk_score': round(total_risk, 2),
            'risk_level': risk_level,
            'gpa': gpa,
            'attendance_rate': attendance_rate,
            'failing_courses': failing_courses,
            'intervention_count': intervention_count,
            'on_probation': on_probation,
            'credits_completed': student.credits_completed or 0,
            'department': student.department or 'Unknown',
            'year': student.year or 0,
            'factors': {
                'gpa': round(gpa_risk, 2),
                'attendance': round(attendance_risk, 2),
                'academic': round(academic_risk, 2),
                'intervention': round(intervention_risk, 2),
                'probation': round(probation_risk, 2)
            },
            'recommendations': get_college_recommendations(risk_level, gpa, failing_courses, on_probation)
        }
    except Exception as e:
        return {
            'risk_score': 0,
            'risk_level': 'Low',
            'error': str(e)
        }

def get_college_recommendations(risk_level, gpa, failing_courses, on_probation):
    """Get college-specific recommendations based on risk factors"""
    recommendations = []
    
    # GPA-based recommendations
    if gpa < 2.0:
        recommendations.extend([
            'Immediate academic probation counseling required',
            'Enroll in academic skills workshop',
            'Meet with academic advisor for course planning',
            'Consider reducing course load for next semester'
        ])
    elif gpa < 2.5:
        recommendations.extend([
            'Weekly academic counseling sessions',
            'Join study groups for difficult courses',
            'Meet with professors during office hours',
            'Utilize tutoring services'
        ])
    elif gpa < 3.0:
        recommendations.extend([
            'Focus on time management skills',
            'Participate in study skills workshops',
            'Consider peer mentoring programs'
        ])
    
    # Failing courses recommendations
    if failing_courses > 0:
        recommendations.extend([
            f'Address {failing_courses} failing course{"s" if failing_courses > 1 else ""} immediately',
            'Meet with course instructors for improvement plan',
            'Request tutoring for specific subjects',
            'Consider withdrawal options if applicable'
        ])
    
    # Attendance-based recommendations
    recommendations.extend([
        'Maintain regular class attendance',
        'Participate actively in class discussions',
        'Form study groups with classmates'
    ])
    
    # Risk level specific recommendations
    if risk_level == 'Critical':
        recommendations.extend([
            'Comprehensive academic intervention plan',
            'Weekly meetings with academic advisor',
            'Mental health counseling support',
            'Financial aid consultation if needed'
        ])
    elif risk_level == 'High':
        recommendations.extend([
            'Bi-weekly academic counseling',
            'Structured study schedule',
            'Regular progress monitoring'
        ])
    elif risk_level == 'Medium':
        recommendations.extend([
            'Monthly progress check-ins',
            'Study skills improvement',
            'Peer mentoring opportunities'
        ])
    else:  # Low risk
        recommendations.extend([
            'Maintain current academic performance',
            'Consider leadership opportunities',
            'Explore advanced coursework options'
        ])
    
    # Remove duplicates and return
    return list(dict.fromkeys(recommendations))

def get_historical_attendance(student_id):
    """Get historical attendance data for charts"""
    # This would typically query real historical data
    return {
        'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'data': [85, 87, 83, 89]
    }

def get_historical_academic(student_id):
    """Get historical academic data for charts"""
    # This would typically query real historical data
    return {
        'labels': ['Test 1', 'Test 2', 'Test 3', 'Test 4'],
        'data': [75, 78, 82, 80]
    }
