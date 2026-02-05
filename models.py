"""
EduGuard Models
Clean, consolidated database models
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='faculty')  # admin, faculty, student, parent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        try:
            return check_password_hash(self.password_hash, password)
        except:
            simple_hash = hashlib.sha256(password.encode()).hexdigest()
            return self.password_hash == simple_hash

    def __repr__(self):
        return f'<User {self.email}>'

class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(50))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    enrollment_date = db.Column(db.Date)
    credits_completed = db.Column(db.Integer, default=0)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    risk_profile = db.relationship('RiskProfile', backref='student', uselist=False, lazy=True)
    counselling_sessions = db.relationship('Counselling', backref='student', lazy=True)
    mentor_assignments = db.relationship('MentorAssignment', backref='student', lazy=True)

    def __repr__(self):
        return f'<Student {self.student_id}>'

class Attendance(db.Model):
    """Attendance model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Late, Excused
    course = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.date}>'

class RiskProfile(db.Model):
    """Risk profile model"""
    __tablename__ = 'risk_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='Low')  # Low, Medium, High, Critical
    attendance_rate = db.Column(db.Float, default=0.0)
    academic_performance = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ML prediction fields
    ml_prediction = db.Column(db.Float)
    ml_confidence = db.Column(db.Float)
    ml_features = db.Column(db.Text)
    
    def __repr__(self):
        return f'<RiskProfile {self.student_id} - {self.risk_level}>'

class Counselling(db.Model):
    """Counselling session model"""
    __tablename__ = 'counselling'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    counsellor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    session_type = db.Column(db.String(50))  # Individual, Group, Crisis
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Completed, Cancelled
    notes = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    
    # Relationships
    counsellor = db.relationship('User', backref='counselling_sessions')

    def __repr__(self):
        return f'<Counselling {self.id} - {self.session_date}>'

class MentorAssignment(db.Model):
    """Mentor assignment model"""
    __tablename__ = 'mentor_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, Completed
    notes = db.Column(db.Text)
    
    # Relationships
    mentor = db.relationship('User', backref='mentor_assignments')

    def __repr__(self):
        return f'<MentorAssignment {self.student_id} - {self.mentor_id}>'

class Alert(db.Model):
    """Alert model for notifications"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    alert_type = db.Column(db.String(50))  # Risk Level Change, Attendance, Academic Performance
    severity = db.Column(db.String(20))  # Critical, High, Medium, Low
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active')  # Active, Resolved, Acknowledged
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_alerts')

    def __repr__(self):
        return f'<Alert {self.id} - {self.alert_type}>'
