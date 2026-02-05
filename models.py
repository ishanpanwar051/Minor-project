from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

# Create shared SQLAlchemy instance
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
        """Check password using both Werkzeug and simple hash methods"""
        try:
            # Try Werkzeug hash first
            return check_password_hash(self.password_hash, password)
        except:
            # Fallback to simple SHA256 hash
            simple_hash = hashlib.sha256(password.encode()).hexdigest()
            return self.password_hash == simple_hash

    def __repr__(self):
        return f'<User {self.email}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)  # College ID/Roll number
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    year = db.Column(db.Integer, nullable=False)  # 1st year, 2nd year, 3rd year, 4th year
    semester = db.Column(db.Integer, nullable=False)  # 1-8 semesters
    department = db.Column(db.String(100))  # Computer Science, Engineering, Business, etc.
    program = db.Column(db.String(100))  # B.Tech, B.Sc, B.Com, etc.
    enrollment_date = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    gpa = db.Column(db.Float, default=0.0)  # Cumulative GPA
    credits_completed = db.Column(db.Integer, default=0)  # Total credits earned
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    academic_records = db.relationship('AcademicRecord', backref='student', lazy=True, cascade='all, delete-orphan')
    interventions = db.relationship('Intervention', backref='student', lazy=True, cascade='all, delete-orphan')
    risk_profile = db.relationship('RiskProfile', backref='student', uselist=False, lazy=True, cascade='all, delete-orphan')

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def academic_standing(self):
        """Calculate academic standing based on GPA"""
        if self.gpa >= 3.5:
            return "Excellent"
        elif self.gpa >= 3.0:
            return "Good"
        elif self.gpa >= 2.0:
            return "Satisfactory"
        else:
            return "At Risk"

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
    course_code = db.Column(db.String(20), nullable=False)  # CS101, MATH201, etc.
    course_name = db.Column(db.String(100), nullable=False)  # Introduction to Programming
    credits = db.Column(db.Float, default=3.0)  # Credit hours
    grade = db.Column(db.String(2))  # A, B, C, D, F
    grade_points = db.Column(db.Float, default=0.0)  # 4.0, 3.0, 2.0, 1.0, 0.0
    semester = db.Column(db.Integer, nullable=False)
    academic_year = db.Column(db.String(9))  # 2023-2024
    exam_date = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text)
    
    def calculate_grade_points(self):
        """Convert letter grade to grade points"""
        grade_mapping = {
            'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0,
            'F': 0.0
        }
        return grade_mapping.get(self.grade, 0.0)
    
    def quality_points(self):
        """Calculate quality points (grade points × credits)"""
        return self.calculate_grade_points() * self.credits

    def __repr__(self):
        return f'<AcademicRecord {self.student_id} - {self.course_code}: {self.grade}>'

class Intervention(db.Model):
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    type = db.Column(db.String(50))  # Academic Counseling, Mental Health Support, Tutoring, Financial Aid, Career Guidance
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Resolved, Cancelled
    notes = db.Column(db.Text)
    assigned_to = db.Column(db.String(100))  # Counselor, Professor, Advisor, Staff
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
    ml_prediction = db.Column(db.Integer)  # 0 or 1 for dropout prediction
    ml_probability = db.Column(db.Float)  # Dropout probability percentage
    ml_confidence = db.Column(db.Float)  # Model confidence score
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

class Counselling(db.Model):
    __tablename__ = 'counselling'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    counselling_type = db.Column(db.String(50))  # Academic, Personal, Career, Mental Health, Financial
    remarks = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, In Progress, Completed, Cancelled
    counsellor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='counselling_sessions')
    counsellor = db.relationship('User', foreign_keys=[counsellor_id], backref='counselling_assigned')
    
    def __repr__(self):
        return f'<Counselling {self.student_id} - {self.counselling_type}>'

class MentorAssignment(db.Model):
    __tablename__ = 'mentor_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assignment_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, Completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mentor = db.relationship('User', foreign_keys=[mentor_id], backref='mentee_assignments')
    student = db.relationship('Student', backref='mentor_assignments')
    
    def __repr__(self):
        return f'<MentorAssignment {self.mentor_id}-{self.student_id}>'

class PerformanceTracker(db.Model):
    __tablename__ = 'performance_tracker'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)  # Mathematics, Physics, etc.
    exam_type = db.Column(db.String(50))  # Midterm, Final, Quiz, Assignment
    before_score = db.Column(db.Float)  # Score before intervention
    after_score = db.Column(db.Float)  # Score after intervention
    max_score = db.Column(db.Float, default=100.0)
    improvement_percentage = db.Column(db.Float)  # Calculated improvement
    exam_date = db.Column(db.Date, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='performance_records')
    
    def calculate_improvement(self):
        """Calculate improvement percentage"""
        if self.max_score > 0:
            improvement = ((self.after_score - self.before_score) / self.max_score) * 100
            self.improvement_percentage = round(improvement, 2)
            return self.improvement_percentage
        return 0.0
    
    def __repr__(self):
        return f'<PerformanceTracker {self.student_id} - {self.subject_name}>'

class StudentReason(db.Model):
    __tablename__ = 'student_reasons'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    financial_reason = db.Column(db.Text)  # Financial difficulties, tuition fees, etc.
    academic_reason = db.Column(db.Text)  # Academic struggles, difficult courses, etc.
    family_reason = db.Column(db.Text)  # Family issues, responsibilities, etc.
    health_reason = db.Column(db.Text)  # Health problems, mental health, etc.
    personal_reason = db.Column(db.Text)  # Personal issues, motivation, etc.
    other_reason = db.Column(db.Text)  # Other reasons not categorized
    severity = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Critical
    status = db.Column(db.String(20), default='Active')  # Active, Resolved, Addressed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    student = db.relationship('Student', backref='reason_records')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_reasons')
    
    def __repr__(self):
        return f'<StudentReason {self.student_id}>'

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    alert_type = db.Column(db.String(50))  # Risk Level Change, Attendance, Academic Performance, Mental Health, Financial Aid
    severity = db.Column(db.String(20))  # Critical, High, Medium, Low
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active')  # Active, Resolved, Acknowledged
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    student = db.relationship('Student', backref='alerts')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_alerts')
    
    def __repr__(self):
        return f'<Alert {self.id} - {self.alert_type}>'
