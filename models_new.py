from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER" 
    STUDENT = "STUDENT"

class AttendanceStatus(enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    EXCUSED = "Excused"

class InterventionType(enum.Enum):
    COUNSELING = "Counseling"
    PARENT_MEETING = "Parent Meeting"
    REMEDIAL_CLASS = "Remedial Class"
    ACADEMIC_SUPPORT = "Academic Support"
    PERSONAL_ISSUE = "Personal Issue"

class InterventionStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"

class RiskLevel(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class User(UserMixin, db.Model):
    """Enhanced User model with security features"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased length for modern hashes
    role = db.Column(db.Enum(UserRole), default=UserRole.TEACHER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user_account', uselist=False, lazy='select')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_user_email_active', 'email', 'is_active'),
        db.Index('idx_user_role_active', 'role', 'is_active'),
    )
    
    def set_password(self, password):
        """Set password with secure hashing"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password):
        """Verify password securely"""
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """Check if account is locked"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def lock_account(self, hours=24):
        """Lock account for specified hours"""
        from datetime import timedelta
        self.locked_until = datetime.utcnow() + timedelta(hours=hours)
        self.failed_login_attempts = 0
    
    def unlock_account(self):
        """Unlock account"""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Lock after 5 attempts
            self.lock_account()
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def is_teacher(self):
        """Check if user is teacher"""
        return self.role == UserRole.TEACHER
    
    def is_student(self):
        """Check if user is student"""
        return self.role == UserRole.STUDENT
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary (for API responses)"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None
            })
        
        return data

class Student(db.Model):
    """Enhanced Student model with proper relationships and constraints"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    semester = db.Column(db.Integer, nullable=False)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Optional user account link
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, unique=True)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    academic_records = db.relationship('AcademicRecord', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    interventions = db.relationship('Intervention', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    risk_profile = db.relationship('RiskProfile', backref='student', uselist=False, cascade='all, delete-orphan')
    
    # Constraints and indexes
    __table_args__ = (
        db.CheckConstraint('semester > 0 AND semester <= 12', name='check_semester_range'),
        db.Index('idx_student_name', 'first_name', 'last_name'),
        db.Index('idx_student_semester', 'semester'),
    )
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_current_risk(self):
        """Get current risk profile"""
        return self.risk_profile
    
    def calculate_attendance_rate(self, days=30):
        """Calculate attendance rate for last N days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        
        total_records = self.attendance_records.filter(Attendance.date >= cutoff_date).count()
        if total_records == 0:
            return 100.0  # Default to 100% if no records
        
        present_records = self.attendance_records.filter(
            Attendance.date >= cutoff_date,
            Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
        ).count()
        
        return (present_records / total_records) * 100.0
    
    def calculate_average_score(self):
        """Calculate average academic score"""
        records = self.academic_records.all()
        if not records:
            return 0.0
        
        total_percentage = 0
        for record in records:
            if record.max_score > 0:
                total_percentage += (record.score / record.max_score) * 100.0
        
        return total_percentage / len(records)
    
    def to_dict(self, include_sensitive=False):
        """Convert student to dictionary"""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'semester': self.semester,
            'enrollment_date': self.enrollment_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
        
        if include_sensitive:
            data['phone'] = self.phone
            data['user_id'] = self.user_id
        
        # Include risk information
        if self.risk_profile:
            data['risk'] = self.risk_profile.to_dict()
        
        return data

class Attendance(db.Model):
    """Enhanced Attendance model with enum and constraints"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(AttendanceStatus), nullable=False)
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'date': self.date.isoformat(),
            'status': self.status.value,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class AcademicRecord(db.Model):
    """Enhanced Academic Record model"""
    __tablename__ = 'academic_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, default=100.0, nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)  # Midterm, Final, Quiz
    date = db.Column(db.Date, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraints and indexes
    __table_args__ = (
        db.CheckConstraint('score >= 0', name='check_score_positive'),
        db.CheckConstraint('max_score > 0', name='check_max_score_positive'),
        db.CheckConstraint('score <= max_score', name='check_score_not_exceed_max'),
        db.CheckConstraint('semester > 0 AND semester <= 12', name='check_semester_range'),
        db.Index('idx_academic_student_subject', 'student_id', 'subject'),
        db.Index('idx_academic_date', 'date'),
        db.Index('idx_academic_semester', 'semester'),
    )
    
    @property
    def percentage(self):
        """Calculate percentage score"""
        if self.max_score > 0:
            return (self.score / self.max_score) * 100.0
        return 0.0
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject': self.subject,
            'score': self.score,
            'max_score': self.max_score,
            'percentage': round(self.percentage, 2),
            'exam_type': self.exam_type,
            'date': self.date.isoformat(),
            'semester': self.semester,
            'created_at': self.created_at.isoformat()
        }

class Intervention(db.Model):
    """Enhanced Intervention model"""
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    type = db.Column(db.Enum(InterventionType), nullable=False)
    notes = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(InterventionStatus), default=InterventionStatus.OPEN, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    follow_up_date = db.Column(db.Date)
    
    # Staff who created the intervention
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='created_interventions', foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        db.Index('idx_intervention_student_status', 'student_id', 'status'),
        db.Index('idx_intervention_date', 'date'),
        db.Index('idx_intervention_creator', 'created_by'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'type': self.type.value,
            'notes': self.notes,
            'status': self.status.value,
            'date': self.date.isoformat(),
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat()
        }

class RiskProfile(db.Model):
    """Enhanced Risk Profile model"""
    __tablename__ = 'risk_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, unique=True)
    risk_score = db.Column(db.Float, default=0.0, nullable=False)
    risk_level = db.Column(db.Enum(RiskLevel), default=RiskLevel.LOW, nullable=False)
    
    # Risk factors
    attendance_factor = db.Column(db.Float, default=0.0)
    academic_factor = db.Column(db.Float, default=0.0)
    behavioral_factor = db.Column(db.Float, default=0.0)
    
    # Additional metrics
    attendance_rate = db.Column(db.Float, default=100.0)
    average_score = db.Column(db.Float, default=100.0)
    
    # Timestamps
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraints and indexes
    __table_args__ = (
        db.CheckConstraint('risk_score >= 0 AND risk_score <= 100', name='check_risk_score_range'),
        db.CheckConstraint('attendance_rate >= 0 AND attendance_rate <= 100', name='check_attendance_rate_range'),
        db.CheckConstraint('average_score >= 0 AND average_score <= 100', name='check_average_score_range'),
        db.Index('idx_risk_score', 'risk_score'),
        db.Index('idx_risk_level', 'risk_level'),
        db.Index('idx_risk_updated', 'last_updated'),
    )
    
    def is_high_risk(self):
        """Check if student is high risk"""
        return self.risk_level == RiskLevel.HIGH
    
    def is_medium_risk(self):
        """Check if student is medium risk"""
        return self.risk_level == RiskLevel.MEDIUM
    
    def is_low_risk(self):
        """Check if student is low risk"""
        return self.risk_level == RiskLevel.LOW
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'risk_score': round(self.risk_score, 2),
            'risk_level': self.risk_level.value,
            'attendance_factor': round(self.attendance_factor, 2),
            'academic_factor': round(self.academic_factor, 2),
            'behavioral_factor': round(self.behavioral_factor, 2),
            'attendance_rate': round(self.attendance_rate, 2),
            'average_score': round(self.average_score, 2),
            'last_updated': self.last_updated.isoformat(),
            'created_at': self.created_at.isoformat()
        }
