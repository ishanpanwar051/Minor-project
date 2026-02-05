"""
Fix for Legacy API Methods in EduGuard System
Updates Flask routes to use modern security patterns
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import functools

# Import updated security models
from models.security import SecurityLog, UserSession
from models import db, User

# Import updated routes
from routes.main_new import main_bp as main_blueprint
from routes.auth_fixed import auth_bp as auth_blueprint
from routes.counselling import counselling_bp as counselling_blueprint
from routes.mentor import mentor_bp as mentor_blueprint
from routes.performance import performance_bp as performance_blueprint
from routes.ml import ml_bp as ml_blueprint
from routes.reason import reason_bp as reason_blueprint
from routes.student import student_bp as student_blueprint

# Import security services
from services.security import validate_email, validate_password, validate_student_id, validate_name, sanitize_input, admin_required, faculty_required, rate_limit, validate_csrf_token, log_security_event

# Import updated configuration
from config_enhanced import Config

# Legacy route fixes
def fix_legacy_api_routes():
    """Fix legacy API routes to use modern security patterns"""
    
    # Fix login route to use proper validation
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            try:
                # Validate form data
                form_data = get_form_data_with_validation(
                    request.form,
                    ['email', 'password']
                )
                
                if not form_data['success']:
                    return render_template('login_standalone.html')
                
                # Find user
                user = User.query.filter_by(email=form_data['data']['email']).first()
                
                if user and user.check_password(form_data['data']['password']):
                    login_user(user, remember=form_data['data'].get('remember', False))
                    
                    # Redirect based on user role
                    if user.role == 'student':
                        student = Student.query.filter_by(user_id=user.id).first()
                        if student:
                            return redirect(url_for('student.student_dashboard'))
                    
                    elif user.role == 'parent':
                        return redirect(url_for('main.dashboard'))
                    
                    else:  # admin or faculty
                        return redirect(url_for('main.dashboard'))
                
            except Exception as e:
                flash(f'Login error: {str(e)}', 'danger')
        
        return render_template('login_standalone.html')
