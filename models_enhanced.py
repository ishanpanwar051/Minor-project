from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
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
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)  # Roll number
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    semester = db.Column(db.Integer, nullable=False)
    enrollment_date = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    academic_records = db.relationship('AcademicRecord', backref='student', lazy=True, cascade='all, delete-orphan')
    interventions = db.relationship('Intervention', backref='student', lazy=True, cascade='all, delete-orphan')
    risk_profile = db.relationship('RiskProfile', backref='student', uselist=False, lazy=True, cascade='all, delete-orphan')

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<Student {self.student_id}>'

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # Present, Absent, Late, Excused
    subject = db.Column(db.String(50))  # Subject for which attendance was taken
    notes = db.Column(db.Text)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'date', 'subject', name='_attendance_uc'),)

    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.date}: {self.status}>'

class AcademicRecord(db.Model):
    __tablename__ = 'academic_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, default=100.0)
    exam_type = db.Column(db.String(50))  # Midterm, Final, Quiz, Assignment
    exam_date = db.Column(db.Date, default=date.today)
    semester = db.Column(db.Integer)
    notes = db.Column(db.Text)
    
    def percentage(self):
        if self.max_score > 0:
            return (self.score / self.max_score) * 100
        return 0

    def __repr__(self):
        return f'<AcademicRecord {self.student_id} - {self.subject}: {self.score}>'

class Intervention(db.Model):
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    type = db.Column(db.String(50))  # Counseling, Parent Meeting, Remedial Class, Academic Support
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Resolved, Cancelled
    notes = db.Column(db.Text)
    assigned_to = db.Column(db.String(100))  # Staff member responsible
    follow_up_date = db.Column(db.Date)
    outcome = db.Column(db.Text)  # Results of the intervention

    def __repr__(self):
        return f'<Intervention {self.student_id} - {self.type}>'

class RiskProfile(db.Model):
    __tablename__ = 'risk_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    risk_score = db.Column(db.Float, default=0.0)  # 0 to 100
    risk_level = db.Column(db.String(20), default='Low')  # Low, Medium, High, Critical
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Risk factors
    attendance_factor = db.Column(db.Float, default=0.0)  # Contribution of attendance to risk
    academic_factor = db.Column(db.Float, default=0.0)  # Contribution of grades to risk
    engagement_factor = db.Column(db.Float, default=0.0)  # Contribution of engagement to risk
    demographic_factor = db.Column(db.Float, default=0.0)  # Contribution of demographic factors
    
    # Computed metrics
    attendance_rate = db.Column(db.Float, default=85.0)  # Attendance percentage
    average_score = db.Column(db.Float, default=75.0)  # Average academic score
    engagement_score = db.Column(db.Float, default=50.0)  # LMS engagement score
    
    # Risk indicators
    consecutive_absences = db.Column(db.Integer, default=0)  # Number of consecutive absences
    failing_subjects = db.Column(db.Integer, default=0)  # Number of failing subjects
    intervention_history = db.Column(db.Integer, default=0)  # Number of previous interventions
    
    def update_risk_level(self):
        """Update risk level based on risk score"""
        if self.risk_score >= 80:
            self.risk_level = 'Critical'
        elif self.risk_score >= 60:
            self.risk_level = 'High'
        elif self.risk_score >= 40:
            self.risk_level = 'Medium'
        else:
            self.risk_level = 'Low'
        self.last_updated = datetime.utcnow()

    def __repr__(self):
        return f'<RiskProfile {self.student_id} - {self.risk_level}>'

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    alert_type = db.Column(db.String(50))  # Attendance, Academic, Behavioral, Risk
    severity = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active')  # Active, Resolved, Dismissed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_alerts')

    def __repr__(self):
        return f'<Alert {self.student_id} - {self.alert_type}>'
