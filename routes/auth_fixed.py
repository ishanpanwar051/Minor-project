from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = bool(request.form.get('remember'))
            
            # Validate input
            if not email or not password:
                flash('Please enter both email and password', 'danger')
                return render_template('login_standalone.html')
            
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                
                # Redirect based on user role
                if user.role == 'student':
                    # Find student profile for this user
                    student = Student.query.filter_by(user_id=user.id).first()
                    if student:
                        return redirect(url_for('main.student_detail', id=student.id))
                    else:
                        return redirect(url_for('main.dashboard'))
                elif user.role == 'parent':
                    return redirect(url_for('main.dashboard'))
                else:  # admin or faculty
                    return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid email or password', 'danger')
                
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
    
    return render_template('login_standalone.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    try:
        logout_user()
        flash('You have been logged out successfully', 'success')
    except Exception as e:
        flash(f'Logout error: {str(e)}', 'danger')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Handle user registration (admin only)"""
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')
            
            # Validate input
            if not all([username, email, password, role]):
                flash('Please fill in all fields', 'danger')
                return render_template('register.html')
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('User with this email already exists', 'danger')
                return render_template('register.html')
            
            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'danger')
                return render_template('register.html')
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                role=role
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'User {email} created successfully!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'danger')
    
    return render_template('register.html')
