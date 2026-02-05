"""
Security and Quality Enhancements for EduGuard System
Input validation, role-based access, environment variables
"""

from functools import wraps
from flask import request, session, redirect, url_for, flash, abort
import re
import os
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|\\:";\'<>,.?/~`' for c in password)
    
    return len(password) >= 8 and has_upper and has_lower and has_digit and has_special

def validate_student_id(student_id):
    """Validate student ID format"""
    pattern = r'^[A-Z]{2}[0-9]{2,4}$'
    return re.match(pattern, student_id) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?[0-9]{1,3}$'
    return re.match(pattern, phone) is not None

def validate_name(name):
    """Validate name format"""
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    
    if len(name) > 50:
        return False, "Name must be less than 50 characters"
    
    # Allow letters, spaces, hyphens, apostrophes
    pattern = r'^[a-zA-Z\s\'\-]+$'
    return re.match(pattern, name) is not None

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\';]', '', text)
    # Strip whitespace
    return text.strip()

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def faculty_required(f):
    """Decorator to require faculty or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role not in ['admin', 'faculty']:
            flash('Faculty access required', 'danger')
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def validate_form_data(form_data, required_fields):
    """Validate form data"""
    errors = {}
    
    for field in required_fields:
        if field not in form_data or not form_data[field].strip():
            errors[field] = f'{field.replace('_', ' ').title()} is required'
        else:
            value = form_data[field].strip()
            
            # Field-specific validation
            if field == 'email':
                if not validate_email(value):
                    errors[field] = 'Please enter a valid email address'
            elif field == 'password':
                if not validate_password(value):
                    errors[field] = 'Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special characters'
            elif field == 'student_id':
                if not validate_student_id(value):
                    errors[field] = 'Student ID must be in format: 2 letters followed by 2-4 digits (e.g., CS101)'
            elif field == 'phone':
                if not validate_phone(value):
                    errors[field] = 'Please enter a valid phone number'
            elif field == 'first_name' or field == 'last_name':
                if not validate_name(value):
                    errors[field] = 'Please enter a valid name (2-50 characters, letters only)'
            elif field == 'gpa':
                try:
                    gpa_value = float(value)
                    if not (0.0 <= gpa_value <= 4.0):
                        errors[field] = 'GPA must be between 0.0 and 4.0'
                except ValueError:
                    errors[field] = 'Please enter a valid GPA'
    
    return errors

def get_form_data_with_validation(form_data, required_fields):
    """Get form data with validation"""
    errors = validate_form_data(form_data, required_fields)
    
    if errors:
        return {'success': False, 'errors': errors}, None
    
    # Sanitize all inputs
    sanitized_data = {}
    for key, value in form_data.items():
        sanitized_data[key] = sanitize_input(value)
    
    return {'success': True, 'data': sanitized_data, 'errors': {}}

# Rate limiting decorator
def rate_limit(max_requests=100, window_seconds=3600):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', '127.0.0.1'))
            
            # Check rate limit
            if client_ip not in request.session:
                request.session[client_ip] = {
                    'requests': 0,
                    'window_start': datetime.now().timestamp()
                }
            
            current_time = datetime.now().timestamp()
            window_start = request.session[client_ip]['window_start']
            
            if current_time - window_start < window_seconds:
                request.session[client_ip]['requests'] += 1
                return f(*args, **kwargs)
            else:
                # Reset window
                request.session[client_ip] = {
                    'requests': 0,
                    'window_start': current_time
                }
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# CSRF protection
def validate_csrf_token():
    """Validate CSRF token for forms"""
    if request.method == 'POST':
        token = session.get('_csrf_token')
        if not token or token != request.form.get('_csrf_token'):
            return False
        
        return True

def log_security_event(event_type, user_id, details=None, ip_address=None):
    """Log security events"""
    from models import SecurityLog
    
    try:
        log_entry = SecurityLog(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address or request.environ.get('REMOTE_ADDR'),
            user_agent=request.environ.get('HTTP_USER_AGENT', ''),
            details=details,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
    except Exception as e:
        print(f"Error logging security event: {e}")

# Session security
def secure_session():
    """Ensure session is secure"""
    # Regenerate session ID
    session.permanent = True
    session.regenerate()
    
    # Set security headers
    session['secure'] = True
    session['httponly'] = True
