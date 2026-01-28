from flask import session, current_app
from flask_login import login_user, logout_user
from models_new import db, User, UserRole
from datetime import datetime, timedelta
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom authentication error"""
    pass

class AuthorizationError(Exception):
    """Custom authorization error"""
    pass

class AuthenticationService:
    """Service for handling authentication and authorization"""
    
    @staticmethod
    def authenticate_user(email, password, remember_me=False):
        """
        Authenticate user with email and password
        
        Args:
            email (str): User email
            password (str): User password
            remember_me (bool): Whether to remember user session
            
        Returns:
            tuple: (success: bool, user: User or None, message: str)
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                logger.warning(f"Login attempt with non-existent email: {email}")
                return False, None, "Invalid email or password"
            
            # Check if account is locked
            if user.is_locked():
                logger.warning(f"Login attempt on locked account: {email}")
                return False, None, "Account is locked. Please try again later."
            
            # Check if account is active
            if not user.is_active:
                logger.warning(f"Login attempt on inactive account: {email}")
                return False, None, "Account is deactivated. Please contact administrator."
            
            # Verify password
            if not user.check_password(password):
                user.increment_failed_login()
                db.session.commit()
                logger.warning(f"Failed login attempt for email: {email}")
                return False, None, "Invalid email or password"
            
            # Successful login
            user.update_last_login()
            db.session.commit()
            
            # Log in user
            login_user(user, remember=remember_me)
            
            # Set additional session data
            session['user_role'] = user.role.value
            session['login_time'] = datetime.utcnow().isoformat()
            
            logger.info(f"User logged in successfully: {email} (Role: {user.role.value})")
            return True, user, "Login successful"
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False, None, "An error occurred during authentication"
    
    @staticmethod
    def logout_user():
        """
        Log out current user
        
        Returns:
            bool: True if successful
        """
        try:
            user_email = None
            if hasattr(current_app, 'login_manager') and current_app.login_manager._get_user():
                user_email = current_app.login_manager._get_user().email
            
            logout_user()
            
            # Clear session data
            session.clear()
            
            logger.info(f"User logged out: {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return False
    
    @staticmethod
    def create_user(username, email, password, role=UserRole.TEACHER):
        """
        Create a new user
        
        Args:
            username (str): Username
            email (str): Email address
            password (str): Password
            role (UserRole): User role
            
        Returns:
            tuple: (success: bool, user: User or None, message: str)
        """
        try:
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                return False, None, "Email already exists"
            
            if User.query.filter_by(username=username).first():
                return False, None, "Username already exists"
            
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False, None, "Invalid email format"
            
            # Validate password strength
            if len(password) < 8:
                return False, None, "Password must be at least 8 characters long"
            
            if not any(c.isupper() for c in password):
                return False, None, "Password must contain at least one uppercase letter"
            
            if not any(c.islower() for c in password):
                return False, None, "Password must contain at least one lowercase letter"
            
            if not any(c.isdigit() for c in password):
                return False, None, "Password must contain at least one digit"
            
            # Create user
            user = User(
                username=username,
                email=email,
                role=role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user created: {email} (Role: {role.value})")
            return True, user, "User created successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"User creation error: {str(e)}")
            return False, None, "An error occurred while creating user"
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Change user password
        
        Args:
            user_id (int): User ID
            current_password (str): Current password
            new_password (str): New password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            # Verify current password
            if not user.check_password(current_password):
                return False, "Current password is incorrect"
            
            # Validate new password
            if len(new_password) < 8:
                return False, "Password must be at least 8 characters long"
            
            if not any(c.isupper() for c in new_password):
                return False, "Password must contain at least one uppercase letter"
            
            if not any(c.islower() for c in new_password):
                return False, "Password must contain at least one lowercase letter"
            
            if not any(c.isdigit() for c in new_password):
                return False, "Password must contain at least one digit"
            
            # Update password
            user.set_password(new_password)
            db.session.commit()
            
            logger.info(f"Password changed for user: {user.email}")
            return True, "Password changed successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Password change error: {str(e)}")
            return False, "An error occurred while changing password"

# Decorators for route protection
def role_required(*allowed_roles):
    """
    Decorator to require specific user roles
    
    Args:
        *allowed_roles: Allowed user roles
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                logger.warning(f"Unauthenticated access attempt to protected route")
                raise AuthorizationError("Authentication required")
            
            if not any(current_user.has_role(role) for role in allowed_roles):
                logger.warning(f"Unauthorized access attempt by user {current_user.email} (Role: {current_user.role.value})")
                raise AuthorizationError("Insufficient permissions")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return role_required(UserRole.ADMIN)(f)

def teacher_required(f):
    """Decorator to require teacher role"""
    return role_required(UserRole.TEACHER)(f)

def student_or_teacher_required(f):
    """Decorator to require student or teacher role"""
    return role_required(UserRole.STUDENT, UserRole.TEACHER)(f)

def student_or_admin_required(f):
    """Decorator to require student or admin role"""
    return role_required(UserRole.STUDENT, UserRole.ADMIN)(f)

def teacher_or_admin_required(f):
    """Decorator to require teacher or admin role"""
    return role_required(UserRole.TEACHER, UserRole.ADMIN)(f)

def resource_owner_or_admin(resource_user_id_attr='user_id'):
    """
    Decorator to allow resource owner or admin access
    
    Args:
        resource_user_id_attr: Attribute name containing user ID in kwargs
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                raise AuthorizationError("Authentication required")
            
            # Admin can access everything
            if current_user.is_admin():
                return f(*args, **kwargs)
            
            # Check if user owns the resource
            resource_user_id = kwargs.get(resource_user_id_attr)
            if resource_user_id and current_user.id == resource_user_id:
                return f(*args, **kwargs)
            
            # Check if student is accessing their own student record
            if current_user.is_student():
                student_id = kwargs.get('student_id')
                if student_id:
                    from models_new import Student
                    student = Student.query.filter_by(user_id=current_user.id).first()
                    if student and student.id == student_id:
                        return f(*args, **kwargs)
            
            raise AuthorizationError("Access denied")
        return decorated_function
    return decorator
