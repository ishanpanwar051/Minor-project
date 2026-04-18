"""
Enhanced Models for AI-Powered Student Management System
Complete database schema for scholarships, AI features, and counselling
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

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
    """Enhanced User model with additional fields"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')  # admin, faculty, student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False, lazy=True)
    ai_interactions = db.relationship('AIInteraction', backref='user', lazy=True)
    # counselling_requests relationship removed to avoid conflict with CounsellingRequest model

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Student(db.Model):
    """Enhanced Student model with comprehensive academic data"""
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
    credits_completed = db.Column(db.Integer, default=0)
    enrollment_date = db.Column(db.Date)
    expected_graduation = db.Column(db.Date)
    
    # Personal Information
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    nationality = db.Column(db.String(50))
    address = db.Column(db.Text)
    
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
    scholarship_applications = db.relationship('ScholarshipApplication', backref='student', lazy=True)
    # risk_profile relationship removed - RiskProfile not defined in this file
    # attendance_records relationship removed - Attendance not defined in this file

    def __repr__(self):
        return f'<Student {self.student_id}>'

class Scholarship(db.Model):
    """Scholarship model with comprehensive details"""
    __tablename__ = 'scholarships'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    
    # Financial Details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    payment_frequency = db.Column(db.String(20))  # Monthly, Semester, Annual
    
    # Eligibility Criteria
    min_gpa = db.Column(db.Float)
    max_income = db.Column(db.Float)
    required_credits = db.Column(db.Integer)
    departments = db.Column(db.Text)  # JSON array of eligible departments
    year_level = db.Column(db.String(20))  # Freshman, Sophomore, etc.
    nationality_requirements = db.Column(db.Text)
    gender_requirements = db.Column(db.String(20))
    
    # Application Details
    application_deadline = db.Column(db.DateTime, nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    required_documents = db.Column(db.Text)  # JSON array
    application_process = db.Column(db.Text)
    
    # Status and Metadata
    status = db.Column(db.Enum(ScholarshipStatus), default=ScholarshipStatus.DRAFT)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # AI Fields
    ai_eligibility_score = db.Column(db.Float, default=0.0)
    ai_popularity_score = db.Column(db.Float, default=0.0)
    ai_tags = db.Column(db.Text)  # JSON array of AI-generated tags
    
    # Relationships
    applications = db.relationship('ScholarshipApplication', backref='scholarship', lazy=True)
    creator = db.relationship('User', backref='created_scholarships', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Scholarship {self.title}>'

class ScholarshipApplication(db.Model):
    """Scholarship application model with comprehensive tracking"""
    __tablename__ = 'scholarship_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarships.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Application Details
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    review_date = db.Column(db.DateTime)
    review_comments = db.Column(db.Text)
    
    # Submitted Information
    personal_statement = db.Column(db.Text)
    financial_justification = db.Column(db.Text)
    additional_documents = db.Column(db.Text)  # JSON array of file paths
    
    # AI Analysis
    ai_eligibility_score = db.Column(db.Float, default=0.0)
    ai_success_probability = db.Column(db.Float, default=0.0)
    ai_recommendations = db.Column(db.Text)
    ai_missing_requirements = db.Column(db.Text)
    
    # Communication
    notification_sent = db.Column(db.Boolean, default=False)
    last_notification_date = db.Column(db.DateTime)
    
    # Relationships
    reviewer = db.relationship('User', backref='reviewed_applications', foreign_keys=[reviewed_by])

    def __repr__(self):
        return f'<Application {self.id} - {self.status}>'

class CounsellingRequest(db.Model):
    """Counselling request management system"""
    __tablename__ = 'counselling_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Request Details
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(CounsellingStatus), default=CounsellingStatus.REQUESTED)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Topic and Type
    counselling_type = db.Column(db.String(50))  # academic, career, personal, financial
    topic = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Scheduling
    preferred_date = db.Column(db.DateTime)
    preferred_time = db.Column(db.String(20))
    scheduled_date = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, default=60)
    
    # Assignment
    assigned_counsellor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_date = db.Column(db.DateTime)
    
    # Session Details
    session_notes = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.DateTime)
    
    # AI Analysis
    ai_sentiment_score = db.Column(db.Float)
    ai_urgency_score = db.Column(db.Float)
    ai_topic_classification = db.Column(db.String(100))
    ai_recommended_actions = db.Column(db.Text)

    # Relationships - Explicit foreign_keys to avoid ambiguity
    user = db.relationship('User', foreign_keys=[user_id], backref='counselling_user_requests', lazy=True)
    student = db.relationship('Student', foreign_keys=[student_id], backref='counselling_student_requests', lazy=True)
    assigned_counsellor = db.relationship('User', foreign_keys=[assigned_counsellor_id], backref='assigned_counsellor_requests', lazy=True)

    def __repr__(self):
        return f'<CounsellingRequest {self.id} - {self.status}>'

class AIInteraction(db.Model):
    """AI Assistant interaction tracking"""
    __tablename__ = 'ai_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Interaction Details
    session_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    interaction_type = db.Column(db.String(50))  # query, recommendation, analysis
    
    # Content
    user_query = db.Column(db.Text)
    ai_response = db.Column(db.Text)
    context_data = db.Column(db.Text)  # JSON object with user context
    
    # AI Analysis
    intent_classification = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    response_quality_rating = db.Column(db.Integer)  # 1-5 rating
    feedback = db.Column(db.Text)
    
    # Performance Metrics
    response_time_ms = db.Column(db.Integer)
    tokens_used = db.Column(db.Integer)

    def __repr__(self):
        return f'<AIInteraction {self.id} - {self.interaction_type}>'

class AnalyticsData(db.Model):
    """System analytics and metrics storage"""
    __tablename__ = 'analytics_data'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # scholarship, application, user, etc.
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    
    # Additional Data
    dimensions = db.Column(db.Text)  # JSON object for multi-dimensional analysis
    source = db.Column(db.String(50))  # manual, automated, ai_generated
    
    # AI Insights
    ai_trend_direction = db.Column(db.String(20))  # increasing, decreasing, stable
    ai_anomaly_score = db.Column(db.Float, default=0.0)
    ai_prediction = db.Column(db.Float)
    ai_confidence = db.Column(db.Float)

    def __repr__(self):
        return f'<AnalyticsData {self.metric_name} - {self.date}>'

class Notification(db.Model):
    """Enhanced notification system"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # scholarship, counselling, system, etc.
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    read_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Action
    action_url = db.Column(db.String(500))
    action_required = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    
    # Priority
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent

    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'

# Import existing models to maintain compatibility
from models import RiskProfile, Attendance, Counselling, MentorAssignment, Alert
