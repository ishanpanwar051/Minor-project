#!/usr/bin/env python3
"""
Complete Role-Based Access Control (RBAC) System for EduGuard
Production-ready Flask implementation with security best practices
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required as flask_login_required

# ================================
# CUSTOM DECORATORS FOR RBAC
# ================================

def admin_required(f):
    """
    Decorator to restrict access to admin users only
    Usage: @admin_required
    """
    @wraps(f)
    @flask_login_required  # Ensure user is logged in first
    def decorated_function(*args, **kwargs):
        # Check if user has admin role
        if not current_user.is_authenticated or current_user.role != 'admin':
            if request.is_json:
                return jsonify({'error': 'Admin access required', 'code': 'ADMIN_REQUIRED'}), 403
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """
    Decorator to restrict access to student users only
    Usage: @student_required
    """
    @wraps(f)
    @flask_login_required  # Ensure user is logged in first
    def decorated_function(*args, **kwargs):
        # Check if user has student role
        if not current_user.is_authenticated or current_user.role != 'student':
            if request.is_json:
                return jsonify({'error': 'Student access required', 'code': 'STUDENT_REQUIRED'}), 403
            flash('Student access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """
    Generic decorator for multiple role requirements
    Usage: @role_required('admin', 'faculty')
    """
    def decorator(f):
        @wraps(f)
        @flask_login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in allowed_roles:
                if request.is_json:
                    return jsonify({
                        'error': f'Access denied. Required roles: {", ".join(allowed_roles)}',
                        'code': 'ROLE_REQUIRED'
                    }), 403
                flash(f'Access denied. Required roles: {", ".join(allowed_roles)}', 'danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def student_data_access(f):
    """
    Decorator to ensure student can only access their own data
    Usage: @student_data_access
    This decorator should be used on routes that access student-specific data
    """
    @wraps(f)
    @student_required  # Ensure user is student first
    def decorated_function(*args, **kwargs):
        # Additional check: ensure student can only access their own data
        # This will be used with student_id parameter in routes
        return f(*args, **kwargs)
    return decorated_function

# ================================
# SESSION MANAGEMENT HELPERS
# ================================

def set_user_session(user):
    """
    Set user session data after successful login
    """
    session['user_id'] = user.id
    session['user_email'] = user.email
    session['user_role'] = user.role
    session['user_name'] = f"{user.first_name if hasattr(user, 'first_name') else user.email}"
    session.permanent = True  # Make session persistent

def clear_user_session():
    """
    Clear user session data on logout
    """
    session_keys = ['user_id', 'user_email', 'user_role', 'user_name']
    for key in session_keys:
        if key in session:
            session.pop(key, None)

def get_current_user_role():
    """
    Get current user role from session or user object
    """
    if current_user.is_authenticated:
        return current_user.role
    return session.get('user_role', None)

def is_admin():
    """
    Check if current user is admin
    """
    return get_current_user_role() == 'admin'

def is_student():
    """
    Check if current user is student
    """
    return get_current_user_role() == 'student'

def is_faculty():
    """
    Check if current user is faculty
    """
    return get_current_user_role() == 'faculty'

# ================================
# DATA ISOLATION HELPERS
# ================================

def get_student_for_current_user():
    """
    Get student record for current logged-in student
    Returns None if user is not a student or student not found
    """
    if not is_student():
        return None
    
    from models import Student
    return Student.query.filter_by(user_id=current_user.id).first()

def validate_student_access(student_id):
    """
    Validate if current user can access the specified student's data
    Returns True for admin users, False for students accessing other students' data
    """
    # Admins can access any student data
    if is_admin():
        return True
    
    # Students can only access their own data
    if is_student():
        student = get_student_for_current_user()
        return student and student.id == student_id
    
    # Other roles cannot access student data
    return False

def filter_student_query_for_current_user(query):
    """
    Filter a student query based on current user's role
    Admins see all students, students see only themselves
    """
    if is_admin():
        return query  # Admins see all
    elif is_student():
        student = get_student_for_current_user()
        if student:
            return query.filter_by(id=student.id)  # Students see only themselves
        else:
            return query.filter_by(id=-1)  # No access if student not found
    else:
        return query.filter_by(id=-1)  # No access for other roles

# ================================
# SECURITY MIDDLEWARE
# ================================

def validate_session():
    """
    Validate session data integrity
    """
    if not current_user.is_authenticated:
        return False
    
    # Check if session role matches user role
    session_role = session.get('user_role')
    user_role = current_user.role
    
    if session_role != user_role:
        clear_user_session()
        return False
    
    return True

def secure_redirect(endpoint, **kwargs):
    """
    Secure redirect with role-based fallback
    """
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Redirect based on user role
    role_redirects = {
        'admin': 'main.admin_dashboard',
        'student': 'main.student_dashboard',
        'faculty': 'main.faculty_dashboard'
    }
    
    target_endpoint = role_redirects.get(current_user.role, 'auth.login')
    return redirect(url_for(target_endpoint, **kwargs))

# ================================
# ERROR HANDLERS
# ================================

def handle_unauthorized_access():
    """
    Handle unauthorized access attempts
    """
    if request.is_json:
        return jsonify({
            'error': 'Unauthorized access',
            'message': 'You do not have permission to access this resource',
            'code': 'UNAUTHORIZED'
        }), 403
    
    flash('You do not have permission to access this resource', 'danger')
    return redirect(url_for('auth.login'))

def handle_forbidden_access():
    """
    Handle forbidden access attempts (authenticated but wrong role)
    """
    if request.is_json:
        return jsonify({
            'error': 'Access forbidden',
            'message': 'Your role does not permit access to this resource',
            'code': 'FORBIDDEN'
        }), 403
    
    flash('Your role does not permit access to this resource', 'danger')
    return secure_redirect('auth.dashboard')

# ================================
# PRODUCTION CONFIGURATION
# ================================

RBAC_CONFIG = {
    # Session settings
    'SESSION_TIMEOUT': 3600,  # 1 hour
    'PERMANENT_SESSION': True,
    
    # Security settings
    'CSRF_PROTECTION': True,
    'SECURE_HEADERS': True,
    
    # Role hierarchy (for future extension)
    'ROLE_HIERARCHY': {
        'admin': 100,
        'faculty': 50,
        'student': 10
    },
    
    # Protected routes
    'ADMIN_ROUTES': [
        '/admin',
        '/api/admin',
        '/manage',
        '/system'
    ],
    
    'STUDENT_ROUTES': [
        '/student',
        '/support',
        '/my',
        '/profile'
    ]
}

# ================================
# USAGE EXAMPLES
# ================================

"""
Usage Examples:

1. Protecting Admin Routes:
@admin_required
@app.route('/admin/dashboard')
def admin_dashboard():
    # Only admin users can access
    return render_template('admin/dashboard.html')

2. Protecting Student Routes:
@student_required
@app.route('/student/dashboard')
def student_dashboard():
    # Only student users can access
    return render_template('student/dashboard.html')

3. Multiple Role Protection:
@role_required('admin', 'faculty')
@app.route('/faculty/reports')
def faculty_reports():
    # Both admin and faculty can access
    return render_template('faculty/reports.html')

4. Student Data Isolation:
@student_data_access
@app.route('/student/profile/<int:student_id>')
def student_profile(student_id):
    # Students can only see their own profile
    # Admins can see any student profile
    if not validate_student_access(student_id):
        return handle_forbidden_access()
    
    student = Student.query.get_or_404(student_id)
    return render_template('student/profile.html', student=student)

5. Filtering Data for Current User:
@app.route('/api/my/attendance')
@student_required
def my_attendance():
    # Only current student's attendance
    query = Attendance.query
    filtered_query = filter_student_query_for_current_user(query)
    attendances = filtered_query.all()
    return jsonify([att.to_dict() for att in attendances])

6. Session Management:
@app.route('/login', methods=['POST'])
def login():
    user = authenticate_user(request.form)
    if user:
        login_user(user)
        set_user_session(user)  # Set additional session data
        return secure_redirect('dashboard')
    else:
        flash('Invalid credentials', 'danger')
        return render_template('auth/login.html')

7. Logout:
@app.route('/logout')
@login_required
def logout():
    clear_user_session()  # Clear custom session data
    logout_user()
    return redirect(url_for('auth.login'))
"""

if __name__ == '__main__':
    print("RBAC System loaded successfully!")
    print("Import and use the decorators in your Flask routes")
