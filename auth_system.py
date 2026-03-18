from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
from datetime import datetime, timedelta
import os

# Enhanced Authentication System
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Role-based access control decorator
def role_required(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please login to access this page', 'danger')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('dashboard.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# JWT Token Generator
def generate_jwt_token(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

# JWT Token Validator
def validate_jwt_token(token):
    """Validate JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Enhanced User Model for Authentication
class User(UserMixin):
    def __init__(self, id, username, email, password_hash, role='student', 
                 is_active=True, profile_picture=None, phone=None, address=None,
                 created_at=None, last_login=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.profile_picture = profile_picture
        self.phone = phone
        self.address = address
        self.created_at = created_at
        self.last_login = last_login
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_jwt_token(self):
        """Get JWT token for user"""
        return generate_jwt_token(self)
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def has_any_role(self, roles):
        """Check if user has any of the specified roles"""
        return self.role in roles
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        # In real implementation, update in database
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'profile_picture': self.profile_picture,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

# Mock User Database (Replace with actual database)
class UserDatabase:
    def __init__(self):
        self.users = {}
        self._create_default_users()
    
    def _create_default_users(self):
        """Create default users for testing"""
        # Admin User
        admin_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        self.users[1] = User(
            id=1,
            username='admin',
            email='admin@eduguard.edu',
            password_hash=admin_password,
            role='admin',
            phone='+1234567890',
            address='Admin Office, Main Campus'
        )
        
        # Faculty User
        faculty_password = generate_password_hash('faculty123', method='pbkdf2:sha256')
        self.users[2] = User(
            id=2,
            username='faculty',
            email='faculty@eduguard.edu',
            password_hash=faculty_password,
            role='teacher',
            phone='+1234567891',
            address='Faculty Room, Block A'
        )
        
        # Student Users
        student_password = generate_password_hash('student123', method='pbkdf2:sha256')
        
        students_data = [
            {'id': 3, 'username': 'john.doe', 'email': 'john.doe@eduguard.edu'},
            {'id': 4, 'username': 'jane.smith', 'email': 'jane.smith@eduguard.edu'},
            {'id': 5, 'username': 'mike.wilson', 'email': 'mike.wilson@eduguard.edu'},
            {'id': 6, 'username': 'sarah.jones', 'email': 'sarah.jones@eduguard.edu'},
            {'id': 7, 'username': 'alex.brown', 'email': 'alex.brown@eduguard.edu'},
            {'id': 8, 'username': 'emma.davis', 'email': 'emma.davis@eduguard.edu'},
            {'id': 9, 'username': 'chris.miller', 'email': 'chris.miller@eduguard.edu'},
            {'id': 10, 'username': 'lisa.anderson', 'email': 'lisa.anderson@eduguard.edu'}
        ]
        
        for student in students_data:
            self.users[student['id']] = User(
                id=student['id'],
                username=student['username'],
                email=student['email'],
                password_hash=student_password,
                role='student',
                phone=f'+123456789{student["id"]}',
                address=f'Dorm Room {student["id"]}, Student Housing'
            )
        
        # Parent User
        parent_password = generate_password_hash('parent123', method='pbkdf2:sha256')
        self.users[11] = User(
            id=11,
            username='parent',
            email='parent@eduguard.edu',
            password_hash=parent_password,
            role='parent',
            phone='+1234567899',
            address='Parent Residence, City'
        )
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.users.get(int(user_id))
    
    def get_user_by_email(self, email):
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def create_user(self, username, email, password, role='student', **kwargs):
        """Create new user"""
        if self.get_user_by_email(email):
            return None, "Email already exists"
        
        if self.get_user_by_username(username):
            return None, "Username already exists"
        
        user_id = max(self.users.keys()) + 1 if self.users else 1
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            created_at=datetime.utcnow(),
            **kwargs
        )
        
        self.users[user_id] = new_user
        return new_user, "User created successfully"
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None, "User not found"
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        return user, "User updated successfully"
    
    def delete_user(self, user_id):
        """Delete user"""
        if user_id in self.users:
            del self.users[user_id]
            return True, "User deleted successfully"
        return False, "User not found"

# Initialize user database
user_db = UserDatabase()

# Enhanced Login Manager
class EnhancedLoginManager(LoginManager):
    def __init__(self, app=None):
        super().__init__(app)
        self.user_callback = self.load_user
    
    def load_user(self, user_id):
        """Load user from database"""
        return user_db.get_user_by_id(user_id)

# Authentication Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Enhanced login with JWT support"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Validate input
        if not email or not password:
            flash('Please enter both email and password', 'danger')
            return render_template('auth/login.html')
        
        # Find user
        user = user_db.get_user_by_email(email)
        
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact administrator', 'danger')
            return render_template('auth/login.html')
        
        # Update last login
        user.update_last_login()
        
        # Login user
        login_user(user, remember=remember_me)
        
        # Generate JWT token
        token = user.get_jwt_token()
        
        # Store token in session
        from flask import session
        session['jwt_token'] = token
        
        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin.admin'))
        elif user.role == 'teacher':
            return redirect(url_for('dashboard.dashboard'))
        elif user.role == 'student':
            return redirect(url_for('dashboard.dashboard'))
        elif user.role == 'parent':
            return redirect(url_for('parent_portal.dashboard'))
        else:
            return redirect(url_for('dashboard.dashboard'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with role selection"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Validate input
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all required fields', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return render_template('auth/register.html')
        
        # Create user
        user, message = user_db.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone=phone,
            address=address
        )
        
        if user:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Enhanced logout with JWT token cleanup"""
    # Clear JWT token from session
    from flask import session
    session.pop('jwt_token', None)
    
    # Logout user
    logout_user()
    
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        phone = request.form.get('phone')
        address = request.form.get('address')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Update basic info
        user, message = user_db.update_user(
            current_user.id,
            phone=phone,
            address=address
        )
        
        # Handle password change
        if new_password:
            if not current_password:
                flash('Please enter current password to change password', 'danger')
                return render_template('auth/edit_profile.html', user=current_user)
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return render_template('auth/edit_profile.html', user=current_user)
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return render_template('auth/edit_profile.html', user=current_user)
            
            if len(new_password) < 8:
                flash('New password must be at least 8 characters long', 'danger')
                return render_template('auth/edit_profile.html', user=current_user)
            
            # Update password
            new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
            user_db.update_user(current_user.id, password_hash=new_password_hash)
            flash('Password updated successfully', 'success')
        
        if message == "User updated successfully":
            flash('Profile updated successfully', 'success')
        else:
            flash(message, 'danger')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', user=current_user)

@auth_bp.route('/api/token', methods=['POST'])
def get_token():
    """API endpoint to get JWT token"""
    email = request.json.get('email')
    password = request.json.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = user_db.get_user_by_email(email)
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account deactivated'}), 401
    
    token = user.get_jwt_token()
    
    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'expires_in': JWT_EXPIRATION_HOURS * 3600
    })

@auth_bp.route('/api/validate', methods=['POST'])
def validate_token():
    """API endpoint to validate JWT token"""
    token = request.json.get('token')
    
    if not token:
        return jsonify({'error': 'Token required'}), 400
    
    payload = validate_jwt_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    user = user_db.get_user_by_id(payload['user_id'])
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    return jsonify({
        'valid': True,
        'user': user.to_dict(),
        'payload': payload
    })

# Admin Routes for User Management
@auth_bp.route('/admin/users')
@role_required('admin')
def admin_users():
    """Admin user management"""
    users = list(user_db.users.values())
    return render_template('admin/users.html', users=users)

@auth_bp.route('/admin/users/create', methods=['GET', 'POST'])
@role_required('admin')
def admin_create_user():
    """Admin create user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        phone = request.form.get('phone')
        address = request.form.get('address')
        is_active = request.form.get('is_active') == 'on'
        
        user, message = user_db.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone=phone,
            address=address,
            is_active=is_active
        )
        
        if user:
            flash('User created successfully', 'success')
            return redirect(url_for('auth.admin_users'))
        else:
            flash(message, 'danger')
            return render_template('admin/create_user.html')
    
    return render_template('admin/create_user.html')

@auth_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def admin_edit_user(user_id):
    """Admin edit user"""
    user = user_db.get_user_by_id(user_id)
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        phone = request.form.get('phone')
        address = request.form.get('address')
        is_active = request.form.get('is_active') == 'on'
        
        updated_user, message = user_db.update_user(
            user_id,
            username=username,
            email=email,
            role=role,
            phone=phone,
            address=address,
            is_active=is_active
        )
        
        if updated_user:
            flash('User updated successfully', 'success')
            return redirect(url_for('auth.admin_users'))
        else:
            flash(message, 'danger')
            return render_template('admin/edit_user.html', user=user)
    
    return render_template('admin/edit_user.html', user=user)

@auth_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@role_required('admin')
def admin_delete_user(user_id):
    """Admin delete user"""
    if user_id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    success, message = user_db.delete_user(user_id)
    
    if success:
        flash('User deleted successfully', 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('auth.admin_users'))

# Password Reset Routes
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        user = user_db.get_user_by_email(email)
        
        if user:
            # In real implementation, send password reset email
            flash('Password reset link has been sent to your email', 'info')
        else:
            flash('If that email exists in our system, a reset link has been sent', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    # In real implementation, validate token and reset password
    return render_template('auth/reset_password.html', token=token)

# Two-Factor Authentication (Future Enhancement)
@auth_bp.route('/2fa/setup')
@login_required
def setup_2fa():
    """Setup two-factor authentication"""
    return render_template('auth/setup_2fa.html')

@auth_bp.route('/2fa/verify')
@login_required
def verify_2fa():
    """Verify two-factor authentication"""
    return render_template('auth/verify_2fa.html')

# Security Headers Middleware
def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# Rate Limiting (Future Enhancement)
def rate_limit(max_requests=100, window=3600):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # In real implementation, use Redis or database for rate limiting
            return f(*args, **kwargs)
        return decorated_function
    return decorator
