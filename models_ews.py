"""
Enhanced Database Models for Early Warning System (EWS)
Student Dropout Prevention System with Advanced Analytics and ML Integration
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    PARENT = "PARENT"
    STUDENT = "STUDENT"
    COUNSELOR = "COUNSELOR"

class AlertType(enum.Enum):
    HIGH_RISK = "HIGH_RISK"
    ATTENDANCE_DECLINE = "ATTENDANCE_DECLINE"
    PERFORMANCE_DROP = "PERFORMANCE_DROP"
    BEHAVIOR_CONCERN = "BEHAVIOR_CONCERN"
    ASSIGNMENT_MISSING = "ASSIGNMENT_MISSING"
    QUIZ_POOR_PERFORMANCE = "QUIZ_POOR_PERFORMANCE"

class AlertStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    ESCALATED = "ESCALATED"

class InterventionStatus(enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class RiskLevel(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# Enhanced User Model with Role Management
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.TEACHER, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Additional fields
    department = db.Column(db.String(100))
    employee_id = db.Column(db.String(20), unique=True)
    profile_image = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user_account', uselist=False, lazy='select')
    created_alerts = db.relationship('Alert', backref='creator', foreign_keys='Alert.created_by')
    interventions = db.relationship('Intervention', backref='assigned_to', foreign_keys='Intervention.assigned_to_id')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_user_email_active', 'email', 'is_active'),
        db.Index('idx_user_role_active', 'role', 'is_active'),
        db.Index('idx_user_department', 'department'),
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_teacher(self):
        return self.role == UserRole.TEACHER
    
    def is_parent(self):
        return self.role == UserRole.PARENT
    
    def is_student(self):
        return self.role == UserRole.STUDENT
    
    def is_counselor(self):
        return self.role == UserRole.COUNSELOR

# Enhanced Student Model with Rich Features
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    
    # Academic Information
    grade = db.Column(db.String(10), nullable=False)
    section = db.Column(db.String(10))
    roll_number = db.Column(db.String(20))
    enrollment_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    
    # Demographics
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    parent_guardian_name = db.Column(db.String(100))
    parent_guardian_phone = db.Column(db.String(20))
    parent_guardian_email = db.Column(db.String(120))
    
    # System Integration
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, unique=True)
    lms_id = db.Column(db.String(50))  # Learning Management System ID
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    academic_records = db.relationship('AcademicRecord', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    interventions = db.relationship('Intervention', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    risk_profiles = db.relationship('RiskProfile', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    performance_trends = db.relationship('PerformanceTrend', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    engagement_metrics = db.relationship('EngagementMetric', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    # Constraints and indexes
    __table_args__ = (
        db.CheckConstraint('grade IS NOT NULL', name='check_grade_not_null'),
        db.Index('idx_student_name', 'first_name', 'last_name'),
        db.Index('idx_student_grade_section', 'grade', 'section'),
        db.Index('idx_student_enrollment', 'enrollment_date'),
    )
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def current_risk_profile(self):
        return self.risk_profiles.order_by(RiskProfile.created_at.desc()).first()
    
    def active_alerts(self):
        return self.alerts.filter_by(status=AlertStatus.ACTIVE).all()
    
    def get_age(self):
        if self.date_of_birth:
            today = datetime.utcnow().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

# Enhanced Attendance Model with Trends
class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Late, Excused
    check_in_time = db.Column(db.Time)
    check_out_time = db.Column(db.Time)
    total_minutes = db.Column(db.Integer)  # Total time in class
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraints and indexes
    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', name='unique_student_date_attendance'),
        db.Index('idx_attendance_student_date', 'student_id', 'date'),
        db.Index('idx_attendance_date_status', 'date', 'status'),
    )

# Enhanced Academic Records with Multiple Assessment Types
class AcademicRecord(db.Model):
    __tablename__ = 'academic_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # Quiz, Assignment, Midterm, Final, Project
    title = db.Column(db.String(200))
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, default=100.0, nullable=False)
    percentage = db.Column(db.Float)
    grade = db.Column(db.String(5))  # A+, A, B+, etc.
    date = db.Column(db.Date, nullable=False)
    semester = db.Column(db.String(20))
    academic_year = db.Column(db.String(20))
    
    # Additional metrics
    submission_time = db.Column(db.DateTime)
    late_submission = db.Column(db.Boolean, default=False)
    plagiarism_score = db.Column(db.Float)  # If applicable
    feedback = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraints and indexes
    __table_args__ = (
        db.CheckConstraint('score >= 0', name='check_score_positive'),
        db.CheckConstraint('max_score > 0', name='check_max_score_positive'),
        db.CheckConstraint('score <= max_score', name='check_score_not_exceed_max'),
        db.Index('idx_academic_student_subject', 'student_id', 'subject'),
        db.Index('idx_academic_date_type', 'date', 'assessment_type'),
        db.Index('idx_academic_semester', 'semester'),
    )
    
    def calculate_percentage(self):
        if self.max_score > 0:
            self.percentage = (self.score / self.max_score) * 100.0
        return self.percentage
    
    def calculate_grade(self):
        if self.percentage >= 95:
            return 'A+'
        elif self.percentage >= 90:
            return 'A'
        elif self.percentage >= 85:
            return 'B+'
        elif self.percentage >= 80:
            return 'B'
        elif self.percentage >= 75:
            return 'C+'
        elif self.percentage >= 70:
            return 'C'
        elif self.percentage >= 65:
            return 'D+'
        elif self.percentage >= 60:
            return 'D'
        else:
            return 'F'

# Enhanced Intervention Model
class Intervention(db.Model):
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Counseling, Parent Meeting, Academic Support, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(InterventionStatus), default=InterventionStatus.PLANNED, nullable=False)
    priority = db.Column(db.String(20), default='Medium')  # High, Medium, Low
    
    # Scheduling
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time)
    duration_minutes = db.Column(db.Integer)
    location = db.Column(db.String(100))
    
    # People involved
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attendees = db.Column(db.Text)  # JSON array of attendee names
    
    # Outcomes
    outcome = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=True)
    follow_up_date = db.Column(db.Date)
    success_rating = db.Column(db.Integer)  # 1-5 scale
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship('User', backref='created_interventions', foreign_keys=[created_by_id])
    
    # Indexes
    __table_args__ = (
        db.Index('idx_intervention_student_status', 'student_id', 'status'),
        db.Index('idx_intervention_date', 'scheduled_date'),
        db.Index('idx_intervention_assigned', 'assigned_to_id'),
    )

# Alert System Model
class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    type = db.Column(db.Enum(AlertType), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False)
    priority = db.Column(db.String(20), default='Medium')
    
    # Alert details
    risk_score = db.Column(db.Float)
    threshold_value = db.Column(db.Float)
    current_value = db.Column(db.Float)
    
    # People involved
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Escalation
    escalated = db.Column(db.Boolean, default=False)
    escalated_at = db.Column(db.DateTime)
    escalation_level = db.Column(db.Integer, default=1)
    
    # Resolution
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolution_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    resolver = db.relationship('User', backref='resolved_alerts', foreign_keys=[resolved_by])
    
    # Indexes
    __table_args__ = (
        db.Index('idx_alert_student_status', 'student_id', 'status'),
        db.Index('idx_alert_type_priority', 'type', 'priority'),
        db.Index('idx_alert_created', 'created_at'),
    )

# Enhanced Risk Profile with Historical Tracking
class RiskProfile(db.Model):
    __tablename__ = 'risk_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, unique=True)
    current_risk_score = db.Column(db.Float, default=0.0, nullable=False)
    risk_level = db.Column(db.Enum(RiskLevel), default=RiskLevel.LOW, nullable=False)
    
    # Risk Factors
    attendance_factor = db.Column(db.Float, default=0.0)
    academic_factor = db.Column(db.Float, default=0.0)
    behavior_factor = db.Column(db.Float, default=0.0)
    engagement_factor = db.Column(db.Float, default=0.0)
    trend_factor = db.Column(db.Float, default=0.0)
    
    # Current Metrics
    attendance_rate = db.Column(db.Float, default=100.0)
    average_score = db.Column(db.Float, default=100.0)
    behavior_score = db.Column(db.Float, default=10.0)
    engagement_score = db.Column(db.Float, default=10.0)
    
    # ML Predictions
    ml_risk_probability = db.Column(db.Float)  # ML model prediction
    ml_confidence = db.Column(db.Float)
    ml_model_version = db.Column(db.String(20))
    
    # Historical Data
    previous_risk_score = db.Column(db.Float)
    risk_trend = db.Column(db.String(20))  # Improving, Declining, Stable
    
    # Timestamps
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraints and indexes
    __table_args__ = (
        db.CheckConstraint('current_risk_score >= 0 AND current_risk_score <= 100', name='check_risk_score_range'),
        db.CheckConstraint('attendance_rate >= 0 AND attendance_rate <= 100', name='check_attendance_rate_range'),
        db.CheckConstraint('average_score >= 0 AND average_score <= 100', name='check_average_score_range'),
        db.Index('idx_risk_score', 'current_risk_score'),
        db.Index('idx_risk_level', 'risk_level'),
        db.Index('idx_risk_updated', 'last_updated'),
    )
    
    def calculate_risk_level(self):
        if self.current_risk_score >= 80:
            return RiskLevel.CRITICAL
        elif self.current_risk_score >= 60:
            return RiskLevel.HIGH
        elif self.current_risk_score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def update_risk_trend(self):
        if self.previous_risk_score:
            if self.current_risk_score > self.previous_risk_score + 5:
                self.risk_trend = 'Declining'
            elif self.current_risk_score < self.previous_risk_score - 5:
                self.risk_trend = 'Improving'
            else:
                self.risk_trend = 'Stable'

# Performance Trends Model
class PerformanceTrend(db.Model):
    __tablename__ = 'performance_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Academic Metrics
    average_score = db.Column(db.Float)
    attendance_rate = db.Column(db.Float)
    assignment_completion_rate = db.Column(db.Float)
    quiz_average = db.Column(db.Float)
    
    # Engagement Metrics
    lms_login_count = db.Column(db.Integer, default=0)
    page_views = db.Column(db.Integer, default=0)
    time_spent_minutes = db.Column(db.Integer, default=0)
    forum_participation = db.Column(db.Integer, default=0)
    
    # Behavioral Metrics
    behavior_score = db.Column(db.Float)
    disciplinary_actions = db.Column(db.Integer, default=0)
    positive_behavior_points = db.Column(db.Integer, default=0)
    
    # Calculated Metrics
    overall_performance_score = db.Column(db.Float)
    engagement_score = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_trend_student_date', 'student_id', 'date'),
        db.Index('idx_trend_date', 'date'),
    )

# Engagement Metrics Model
class EngagementMetric(db.Model):
    __tablename__ = 'engagement_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # LMS Engagement
    lms_login_count = db.Column(db.Integer, default=0)
    lms_time_spent_minutes = db.Column(db.Integer, default=0)
    course_page_views = db.Column(db.Integer, default=0)
    video_watch_time_minutes = db.Column(db.Integer, default=0)
    
    # Assignment Engagement
    assignments_submitted = db.Column(db.Integer, default=0)
    assignments_total = db.Column(db.Integer, default=0)
    on_time_submissions = db.Column(db.Integer, default=0)
    late_submissions = db.Column(db.Integer, default=0)
    
    # Quiz Engagement
    quizzes_attempted = db.Column(db.Integer, default=0)
    quiz_average_score = db.Column(db.Float)
    quiz_completion_time_minutes = db.Column(db.Float)
    
    # Forum/Community Engagement
    forum_posts = db.Column(db.Integer, default=0)
    forum_comments = db.Column(db.Integer, default=0)
    helpful_votes_received = db.Column(db.Integer, default=0)
    
    # Calculated Scores
    engagement_score = db.Column(db.Float, default=0.0)
    participation_score = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_engagement_student_date', 'student_id', 'date'),
        db.Index('idx_engagement_score', 'engagement_score'),
    )

# System Logs for Audit Trail
class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))  # Student, Alert, Intervention, etc.
    resource_id = db.Column(db.Integer)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='logs')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_log_user_action', 'user_id', 'action'),
        db.Index('idx_log_created', 'created_at'),
        db.Index('idx_log_resource', 'resource_type', 'resource_id'),
    )
