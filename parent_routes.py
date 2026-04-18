from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student, Attendance, RiskProfile
from models_parent import ParentMessage
from datetime import datetime, timedelta
import sqlalchemy as sa

parent_bp = Blueprint('parent', __name__, url_prefix='/parent')

@parent_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Parent login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter email and password', 'danger')
            return render_template('parent_login.html')
        
        # Try to find existing parent user
        user = User.query.filter_by(email=email, role='parent').first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('parent.dashboard'))
        
        # If no user exists, try to find student by parent email and create user
        student = Student.query.filter_by(parent_email=email).first()
        if student and password == 'parent123':  # Default password for auto-created accounts
            # Create parent user account
            user = User(
                username=f"parent_{student.id}",
                email=email,
                role='parent'
            )
            user.set_password('parent123')
            db.session.add(user)
            
            try:
                db.session.commit()
                login_user(user)
                flash('Login successful! Please change your password.', 'success')
                return redirect(url_for('parent.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('Error creating account. Please try again.', 'danger')
                return render_template('parent_login.html')
        
        flash('Invalid email or password', 'danger')
    
    return render_template('parent_login.html')

@parent_bp.route('/dashboard')
@login_required
def dashboard():
    """Parent dashboard showing child's information"""
    if current_user.role != 'parent':
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Find student using parent email
    student = Student.query.filter_by(parent_email=current_user.email).first()
    if not student:
        flash('No student found associated with your email', 'danger')
        return redirect(url_for('parent.login'))
    
    # Get attendance data (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    attendance_records = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.date >= thirty_days_ago
    ).order_by(Attendance.date.desc()).limit(10).all()
    
    # Calculate attendance percentage
    total_classes = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.date >= thirty_days_ago
    ).count()
    present_classes = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.date >= thirty_days_ago,
        Attendance.status == 'Present'
    ).count()
    
    attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
    
    # Get risk profile
    risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
    
    # Get unread message count
    unread_count = ParentMessage.query.filter(
        ParentMessage.student_id == student.id,
        ParentMessage.sender_role == 'faculty',
        ParentMessage.is_read == False
    ).count()
    
    return render_template('parent_dashboard.html', 
                         student=student, 
                         attendance_records=attendance_records,
                         attendance_percentage=attendance_percentage,
                         risk_profile=risk_profile,
                         unread_count=unread_count)

@parent_bp.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    """Parent messaging system"""
    if current_user.role != 'parent':
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Find student
    student = Student.query.filter_by(parent_email=current_user.email).first()
    if not student:
        flash('No student found', 'danger')
        return redirect(url_for('parent.dashboard'))
    
    if request.method == 'POST':
        message_text = request.form.get('message')
        if message_text:
            # Create new message from parent
            message = ParentMessage(
                student_id=student.id,
                sender_role='parent',
                sender_name=current_user.email,
                message=message_text
            )
            db.session.add(message)
            
            try:
                db.session.commit()
                flash('Message sent successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error sending message', 'danger')
        
        return redirect(url_for('parent.messages'))
    
    # Get all messages for this student
    messages = ParentMessage.query.filter_by(student_id=student.id).order_by(ParentMessage.sent_at.asc()).all()
    
    # Mark faculty messages as read
    unread_messages = ParentMessage.query.filter(
        ParentMessage.student_id == student.id,
        ParentMessage.sender_role == 'faculty',
        ParentMessage.is_read == False
    ).all()
    
    for msg in unread_messages:
        msg.is_read = True
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    
    return render_template('parent_messages.html', student=student, messages=messages)

@parent_bp.route('/logout')
@login_required
def logout():
    """Parent logout"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('parent.login'))

@parent_bp.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    """API endpoint for sending messages"""
    if current_user.role != 'parent':
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(parent_email=current_user.email).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    message_text = request.json.get('message')
    if not message_text:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        message = ParentMessage(
            student_id=student.id,
            sender_role='parent',
            sender_name=current_user.email,
            message=message_text
        )
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'timestamp': message.sent_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send message'}), 500
