#!/usr/bin/env python3
"""
Admin Routes with Complete RBAC Protection
Production-ready admin panel with role-based access control
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Student, Attendance, RiskProfile, Alert
from rbac_system import admin_required, role_required, filter_student_query_for_current_user
from sqlalchemy import func, desc
from datetime import datetime, date, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Admin Dashboard - Complete system overview
    Only accessible by admin users
    """
    # Get system statistics
    stats = {
        'total_users': User.query.count(),
        'total_students': Student.query.count(),
        'total_faculty': User.query.filter_by(role='faculty').count(),
        'total_admins': User.query.filter_by(role='admin').count(),
        'total_attendance': Attendance.query.count(),
        'total_alerts': Alert.query.count(),
        'active_alerts': Alert.query.filter_by(status='Active').count()
    }
    
    # Get recent students
    recent_students = Student.query.order_by(desc(Student.enrollment_date)).limit(5).all()
    
    # Get active alerts
    active_alerts = Alert.query.filter_by(status='Active').order_by(desc(Alert.created_at)).limit(5).all()
    
    # Get risk distribution
    risk_stats = db.session.query(
        RiskProfile.risk_level,
        func.count(RiskProfile.id).label('count')
    ).group_by(RiskProfile.risk_level).all()
    
    risk_distribution = {level: count for level, count in risk_stats}
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_students=recent_students,
                         active_alerts=active_alerts,
                         risk_distribution=risk_distribution)

@admin_bp.route('/students')
@admin_required
def students():
    """
    View all students - Admin only
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get all students with pagination
    students = Student.query.order_by(Student.last_name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/students.html', students=students)

@admin_bp.route('/students/<int:student_id>')
@admin_required
def student_detail(student_id):
    """
    View detailed student information - Admin only
    """
    student = Student.query.get_or_404(student_id)
    
    # Get student's attendance records
    attendance_records = Attendance.query.filter_by(student_id=student_id)\
        .order_by(desc(Attendance.date)).limit(30).all()
    
    # Get student's risk profile
    risk_profile = RiskProfile.query.filter_by(student_id=student_id).first()
    
    # Get student's alerts
    alerts = Alert.query.filter_by(student_id=student_id)\
        .order_by(desc(Alert.created_at)).limit(10).all()
    
    # Get student's user account
    user = User.query.get(student.user_id) if student.user_id else None
    
    return render_template('admin/student_detail.html',
                         student=student,
                         user=user,
                         attendance_records=attendance_records,
                         risk_profile=risk_profile,
                         alerts=alerts)

@admin_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    """
    Edit student information - Admin only
    """
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        # Get form data
        student.first_name = request.form.get('first_name', '').strip()
        student.last_name = request.form.get('last_name', '').strip()
        student.email = request.form.get('email', '').strip()
        student.department = request.form.get('department', '').strip()
        student.year = int(request.form.get('year', 1))
        student.semester = int(request.form.get('semester', 1))
        student.gpa = float(request.form.get('gpa', 0.0))
        student.credits_completed = int(request.form.get('credits_completed', 0))
        student.parent_name = request.form.get('parent_name', '').strip()
        student.parent_email = request.form.get('parent_email', '').strip()
        student.parent_phone = request.form.get('parent_phone', '').strip()
        
        try:
            db.session.commit()
            flash('Student information updated successfully!', 'success')
            return redirect(url_for('admin.student_detail', student_id=student_id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating student information. Please try again.', 'danger')
            print(f"Student update error: {e}")
    
    return render_template('admin/edit_student.html', student=student)

@admin_bp.route('/students/<int:student_id>/delete', methods=['POST'])
@admin_required
def delete_student(student_id):
    """
    Delete student - Admin only
    """
    student = Student.query.get_or_404(student_id)
    
    try:
        # Delete related records first
        Attendance.query.filter_by(student_id=student_id).delete()
        RiskProfile.query.filter_by(student_id=student_id).delete()
        Alert.query.filter_by(student_id=student_id).delete()
        
        # Delete student
        db.session.delete(student)
        db.session.commit()
        
        flash('Student deleted successfully!', 'success')
        return redirect(url_for('admin.students'))
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting student. Please try again.', 'danger')
        print(f"Student deletion error: {e}")
        return redirect(url_for('admin.student_detail', student_id=student_id))

@admin_bp.route('/users')
@admin_required
def users():
    """
    View all users - Admin only
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get all users with pagination
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """
    Edit user information - Admin only
    """
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Get form data
        user.username = request.form.get('username', '').strip()
        user.email = request.form.get('email', '').strip()
        user.role = request.form.get('role', 'student')
        
        # Password change (optional)
        new_password = request.form.get('password', '').strip()
        if new_password:
            user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('User information updated successfully!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating user information. Please try again.', 'danger')
            print(f"User update error: {e}")
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/alerts')
@admin_required
def alerts():
    """
    View all alerts - Admin only
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get alerts with pagination
    alerts = Alert.query.order_by(desc(Alert.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/alerts.html', alerts=alerts)

@admin_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
@admin_required
def resolve_alert(alert_id):
    """
    Resolve alert - Admin only
    """
    alert = Alert.query.get_or_404(alert_id)
    
    try:
        alert.status = 'Resolved'
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = current_user.id
        
        db.session.commit()
        flash('Alert resolved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error resolving alert. Please try again.', 'danger')
        print(f"Alert resolution error: {e}")
    
    return redirect(url_for('admin.alerts'))

@admin_bp.route('/reports')
@admin_required
def reports():
    """
    Generate reports - Admin only
    """
    # Get report parameters
    report_type = request.args.get('type', 'overview')
    
    if report_type == 'attendance':
        # Attendance report
        thirty_days_ago = date.today() - timedelta(days=30)
        attendance_data = db.session.query(
            Student.first_name,
            Student.last_name,
            Student.student_id,
            func.count(Attendance.id).label('total_days'),
            func.sum(func.case([(Attendance.status == 'Present', 1)], else_=0)).label('present_days')
        ).join(Attendance)\
         .filter(Attendance.date >= thirty_days_ago)\
         .group_by(Student.id)\
         .all()
        
        return render_template('admin/reports/attendance.html', data=attendance_data)
    
    elif report_type == 'risk':
        # Risk assessment report
        risk_data = db.session.query(
            Student.first_name,
            Student.last_name,
            Student.student_id,
            RiskProfile.risk_level,
            RiskProfile.risk_score,
            RiskProfile.attendance_rate,
            RiskProfile.academic_performance
        ).join(RiskProfile)\
         .order_by(desc(RiskProfile.risk_score))\
         .all()
        
        return render_template('admin/reports/risk.html', data=risk_data)
    
    else:
        # Overview report
        return render_template('admin/reports/overview.html')

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """
    API endpoint for dashboard statistics - Admin only
    """
    # Get current statistics
    stats = {
        'total_students': Student.query.count(),
        'active_alerts': Alert.query.filter_by(status='Active').count(),
        'at_risk_students': db.session.query(RiskProfile)\
            .filter(RiskProfile.risk_level.in_(['High', 'Critical']))\
            .count(),
        'avg_attendance': db.session.query(func.avg(RiskProfile.attendance_rate))\
            .scalar() or 0,
        'avg_gpa': db.session.query(func.avg(Student.gpa)).scalar() or 0
    }
    
    return jsonify(stats)

@admin_bp.route('/api/students/search')
@admin_required
def api_search_students():
    """
    API endpoint for student search - Admin only
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    # Search students
    students = Student.query.filter(
        (Student.first_name.ilike(f'%{query}%')) |
        (Student.last_name.ilike(f'%{query}%')) |
        (Student.student_id.ilike(f'%{query}%')) |
        (Student.email.ilike(f'%{query}%'))
    ).limit(10).all()
    
    results = [{
        'id': student.id,
        'name': f"{student.first_name} {student.last_name}",
        'student_id': student.student_id,
        'email': student.email,
        'department': student.department
    } for student in students]
    
    return jsonify(results)

# Error handlers for admin blueprint
@admin_bp.errorhandler(403)
def forbidden(error):
    flash('Access denied. Admin privileges required.', 'danger')
    return redirect(url_for('auth.login'))

@admin_bp.errorhandler(404)
def not_found(error):
    return render_template('admin/404.html'), 404
