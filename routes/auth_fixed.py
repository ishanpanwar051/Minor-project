from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Only Admin can register new users
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_str = request.form.get('role')
        
        # Convert string role to valid role
        valid_roles = ['admin', 'faculty', 'student', 'parent']
        if role_str not in valid_roles:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register'))
            
        # Validation for Student role
        if role_str == 'student':
            student_record = Student.query.filter_by(email=email).first()
            if not student_record:
                flash(f'No Student record found with email {email}. Please create the student profile first.', 'warning')
                return redirect(url_for('auth.register'))

        new_user = User(
            username=username, 
            email=email, 
            role=role_str
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # If student, link user_id
        if role_str == 'student' and student_record:
            student_record.user_id = new_user.id
            db.session.commit()
        
        flash('User created successfully.', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('main.my_profile'))
        elif current_user.role == 'parent':
            return redirect(url_for('main.dashboard'))  # Fallback for parent
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        current_app.logger.info(f'User {user.email} logged in successfully')
        
        if user.role == 'student':
            return redirect(url_for('main.my_profile'))
        elif user.role == 'parent':
            return redirect(url_for('main.dashboard'))  # Fallback for parent
            
        return redirect(url_for('main.dashboard'))
        
    return render_template('login_standalone.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
