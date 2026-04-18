#!/usr/bin/env python3
"""
Authentication Routes with RBAC Integration
Production-ready Flask authentication system
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student
from rbac_system import set_user_session, clear_user_session, is_admin, is_student, secure_redirect
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login with role-based session management
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return secure_redirect('dashboard')
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'
        
        # Validation
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('auth/login.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Successful login
            login_user(user, remember=remember)
            
            # Set role-based session data
            set_user_session(user)
            
            # Log the login
            print(f"User logged in: {user.email} (Role: {user.role})")
            
            # Flash welcome message based on role
            if user.role == 'admin':
                flash('Welcome, Administrator!', 'success')
            elif user.role == 'student':
                flash('Welcome back, Student!', 'success')
            elif user.role == 'faculty':
                flash('Welcome, Faculty Member!', 'success')
            else:
                flash('Welcome back!', 'success')
            
            # Redirect based on role
            return secure_redirect('dashboard')
        else:
            # Failed login
            flash('Invalid email or password', 'danger')
            print(f"Failed login attempt: {email}")
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Handle user logout with session cleanup
    """
    user_email = current_user.email
    user_role = current_user.role
    
    # Clear custom session data
    clear_user_session()
    
    # Logout user
    logout_user()
    
    # Log the logout
    print(f"User logged out: {user_email} (Role: {user_role})")
    
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration (if enabled)
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return secure_redirect('dashboard')
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', 'student')  # Default to student
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('auth/register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                role=role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            print(f"Registration error: {e}")
    
    return render_template('auth/register.html')

@auth_bp.route('/profile')
@login_required
def profile():
    """
    User profile page with role-based content
    """
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role,
        'created_at': current_user.created_at
    }
    
    # Add role-specific data
    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            user_data.update({
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'department': student.department,
                'year': student.year,
                'gpa': student.gpa
            })
    
    return render_template('auth/profile.html', user=user_data)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change user password
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('auth/change_password.html')
        
        # Verify current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long', 'danger')
            return render_template('auth/change_password.html')
        
        # Update password
        try:
            current_user.set_password(new_password)
            db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Password change failed. Please try again.', 'danger')
            print(f"Password change error: {e}")
    
    return render_template('auth/change_password.html')

@auth_bp.route('/check-session')
def check_session():
    """
    Check current session status (for AJAX calls)
    """
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user_id': current_user.id,
            'email': current_user.email,
            'role': current_user.role,
            'session_valid': True
        })
    else:
        return jsonify({
            'authenticated': False,
            'session_valid': False
        })

# Error handlers for auth blueprint
@auth_bp.errorhandler(404)
def not_found(error):
    return render_template('auth/404.html'), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('auth/500.html'), 500
