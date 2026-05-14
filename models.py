"""
EduGuard Models
Unified database models for the entire system
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import enum
import hashlib
import json

db = SQLAlchemy()

# Enums
class ScholarshipStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    EXPIRED = "expired"

class ApplicationStatus(enum.Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class CounsellingStatus(enum.Enum):
    REQUESTED = "requested"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')  # admin, faculty, student, parent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False, lazy=True)
    ai_interactions = db.relationship('AIInteraction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Student(db.Model):
    """Enhanced Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    
    # Academic Information
    department = db.Column(db.String(50))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    behavior_score = db.Column(db.Float, default=7.0)
    enrollment_date = db.Column(db.Date)
    expected_graduation = db.Column(db.Date)
    credits_completed = db.Column(db.Integer, default=0)
    
    # Personal Information
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    nationality = db.Column(db.String(50))
    address = db.Column(db.Text)
    
    # Parent/Guardian Info
    parent_name = db.Column(db.String(100))
    parent_email = db.Column(db.String(120))
    parent_phone = db.Column(db.String(20))
    
    # Financial Information
    annual_income = db.Column(db.Float)
    financial_need_level = db.Column(db.String(20))  # Low, Medium, High
    employment_status = db.Column(db.String(20))
    
    # Academic Performance
    attendance_rate = db.Column(db.Float, default=0.0)
    academic_standing = db.Column(db.String(20))  # Good, Probation, etc.
    
    # AI Profile
    ai_profile_score = db.Column(db.Float, default=0.0)
    learning_style = db.Column(db.String(50))
    career_interests = db.Column(db.Text)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    risk_profile = db.relationship('RiskProfile', backref='student', uselist=False, lazy=True)
    counselling_sessions = db.relationship('Counselling', backref='student', lazy=True)
    mentor_assignments = db.relationship('MentorAssignment', backref='student', lazy=True)
    scholarship_applications = db.relationship('ScholarshipApplication', backref='student', lazy=True)

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
    risk_reasons = db.Column(db.Text)
    
    financial_issues = db.Column(db.Boolean, default=False)
    family_problems = db.Column(db.Boolean, default=False)
    health_issues = db.Column(db.Boolean, default=False)
    social_isolation = db.Column(db.Boolean, default=False)
    mental_wellbeing_score = db.Column(db.Float, default=10.0)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    ml_prediction = db.Column(db.Float)
    ml_confidence = db.Column(db.Float)
    ml_features = db.Column(db.Text)
    
    def update_risk_score(self, use_ml=True):
        try:
            from enhanced_ai_predictor import risk_predictor
            student_data = {
                'gpa': self.student.gpa or 0,
                'attendance_rate': self.attendance_rate or 0,
                'academic_performance': self.academic_performance or 0,
                'credits_completed': self.student.credits_completed or 0,
                'year': self.student.year or 1,
                'semester': self.student.semester or 1,
                'financial_issues': self.financial_issues or False,
                'family_problems': self.family_problems or False,
                'health_issues': self.health_issues or False,
                'social_isolation': self.social_isolation or False,
                'mental_wellbeing_score': self.mental_wellbeing_score or 10
            }
            
            if use_ml and risk_predictor.is_trained:
                prediction = risk_predictor.predict_risk(student_data)
                self.risk_score = prediction['risk_score']
                self.risk_level = prediction['risk_level']
                self.ml_prediction = prediction['risk_score']
                self.ml_confidence = prediction['confidence']
                self.ml_features = str(prediction['ml_features'])
            else:
                self._rule_based_calculation()
        except Exception:
            self._rule_based_calculation()
        
        self.last_updated = datetime.utcnow()
    
    def _rule_based_calculation(self):
        academic_risk = max(0, 100 - (self.academic_performance or 0)) * 0.3
        attendance_risk = max(0, 100 - (self.attendance_rate or 0)) * 0.3
        personal_risk = 0
        if self.financial_issues: personal_risk += 15
        if self.family_problems: personal_risk += 15
        if self.health_issues: personal_risk += 15
        if self.social_isolation: personal_risk += 10
        personal_risk += max(0, (10 - (self.mental_wellbeing_score or 10))) * 2
        personal_risk = min(40, personal_risk)
        self.risk_score = academic_risk + attendance_risk + personal_risk
        
        reasons = []
        if (self.attendance_rate or 0) < 75: reasons.append('Low attendance (<75%)')
        if (self.academic_performance or 0) < 40: reasons.append('Poor marks (<40)')
        if self.financial_issues: reasons.append('Financial condition: Low')
        if self.family_problems: reasons.append('Family pressure: High')
        if self.health_issues: reasons.append('Health issue present')
        if (self.mental_wellbeing_score or 10) <= 4: reasons.append('High mental stress')
        self.risk_reasons = ', '.join(reasons) if reasons else 'No significant risk factors detected'
        
        personal_flags = sum([1 if f else 0 for f in [self.financial_issues, self.family_problems, self.health_issues, self.social_isolation, (self.mental_wellbeing_score or 10) <= 4]])
        if ((self.attendance_rate or 0) < 60) or ((self.academic_performance or 0) < 30):
            self.risk_level = 'Critical' if personal_flags >= 2 else 'High'
        elif personal_flags >= 3:
            self.risk_level = 'High'
        else:
            self.risk_level = 'Low'

class Counselling(db.Model):
    """Counselling session model (legacy)"""
    __tablename__ = 'counselling'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    counsellor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    session_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Scheduled')
    notes = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    counsellor = db.relationship('User', backref='counselling_sessions')

class MentorAssignment(db.Model):
    """Mentor assignment model"""
    __tablename__ = 'mentor_assignments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Active')
    notes = db.Column(db.Text)
    mentor = db.relationship('User', backref='mentor_assignments')

class Alert(db.Model):
    """Alert model for notifications (legacy)"""
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    alert_type = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_alerts')

# --- Enhanced Models classes from models_enhanced.py ---

class Scholarship(db.Model):
    """Scholarship model"""
    __tablename__ = 'scholarships'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    payment_frequency = db.Column(db.String(20))
    min_gpa = db.Column(db.Float)
    max_income = db.Column(db.Float)
    required_credits = db.Column(db.Integer)
    departments = db.Column(db.Text)
    year_level = db.Column(db.String(20))
    nationality_requirements = db.Column(db.Text)
    gender_requirements = db.Column(db.String(20))
    application_deadline = db.Column(db.DateTime, nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    required_documents = db.Column(db.Text)
    application_process = db.Column(db.Text)
    status = db.Column(db.Enum(ScholarshipStatus), default=ScholarshipStatus.DRAFT)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    ai_eligibility_score = db.Column(db.Float, default=0.0)
    ai_popularity_score = db.Column(db.Float, default=0.0)
    ai_tags = db.Column(db.Text)
    applications = db.relationship('ScholarshipApplication', backref='scholarship', lazy=True)
    creator = db.relationship('User', backref='created_scholarships', foreign_keys=[created_by])

class ScholarshipApplication(db.Model):
    """Scholarship application model"""
    __tablename__ = 'scholarship_applications'
    id = db.Column(db.Integer, primary_key=True)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarships.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    review_date = db.Column(db.DateTime)
    review_comments = db.Column(db.Text)
    personal_statement = db.Column(db.Text)
    financial_justification = db.Column(db.Text)
    additional_documents = db.Column(db.Text)
    ai_eligibility_score = db.Column(db.Float, default=0.0)
    ai_success_probability = db.Column(db.Float, default=0.0)
    ai_recommendations = db.Column(db.Text)
    ai_missing_requirements = db.Column(db.Text)
    notification_sent = db.Column(db.Boolean, default=False)
    last_notification_date = db.Column(db.DateTime)
    reviewer = db.relationship('User', backref='reviewed_applications', foreign_keys=[reviewed_by])
    gpa_at_application = db.Column(db.Float)

class CounsellingRequest(db.Model):
    """Counselling request system"""
    __tablename__ = 'counselling_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(CounsellingStatus), default=CounsellingStatus.REQUESTED)
    priority = db.Column(db.String(20), default='medium')
    counselling_type = db.Column(db.String(50))
    topic = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    preferred_date = db.Column(db.DateTime)
    preferred_time = db.Column(db.String(20))
    scheduled_date = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, default=60)
    assigned_counsellor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_date = db.Column(db.DateTime)
    session_notes = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.DateTime)
    ai_sentiment_score = db.Column(db.Float)
    ai_urgency_score = db.Column(db.Float)
    ai_topic_classification = db.Column(db.String(100))
    ai_recommended_actions = db.Column(db.Text)
    user = db.relationship('User', foreign_keys=[user_id], backref='counselling_user_requests', lazy=True)
    student = db.relationship('Student', foreign_keys=[student_id], backref='counselling_student_requests', lazy=True)
    assigned_counsellor = db.relationship('User', foreign_keys=[assigned_counsellor_id], backref='assigned_counsellor_requests', lazy=True)

class AIInteraction(db.Model):
    """AI Interaction model"""
    __tablename__ = 'ai_interactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    interaction_type = db.Column(db.String(50))
    user_query = db.Column(db.Text)
    ai_response = db.Column(db.Text)
    context_data = db.Column(db.Text)
    intent_classification = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    response_quality_rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    response_time_ms = db.Column(db.Integer)
    tokens_used = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime)

class AnalyticsData(db.Model):
    """Analytics data model"""
    __tablename__ = 'analytics_data'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    dimensions = db.Column(db.Text)
    source = db.Column(db.String(50))
    ai_trend_direction = db.Column(db.String(20))
    ai_anomaly_score = db.Column(db.Float, default=0.0)
    ai_prediction = db.Column(db.Float)
    ai_confidence = db.Column(db.Float)

class Notification(db.Model):
    """Notification model"""
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    read_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    action_url = db.Column(db.String(500))
    action_required = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    priority = db.Column(db.String(20), default='medium')
