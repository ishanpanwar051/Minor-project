from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='faculty')  # admin, faculty, student

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False) # Roll number
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    semester = db.Column(db.Integer, nullable=False)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    academic_records = db.relationship('AcademicRecord', backref='student', lazy=True)
    interventions = db.relationship('Intervention', backref='student', lazy=True)
    risk_profile = db.relationship('RiskProfile', backref='student', uselist=False, lazy=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False) # Present, Absent, Late, Excused

class AcademicRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, default=100.0)
    exam_type = db.Column(db.String(50)) # Midterm, Final, Quiz
    date = db.Column(db.Date, default=datetime.utcnow)

class Intervention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    type = db.Column(db.String(50)) # Counseling, Parent Meeting, Remedial Class
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open') # Open, In Progress, Resolved

class RiskProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    risk_score = db.Column(db.Float, default=0.0) # 0 to 100
    risk_level = db.Column(db.String(20), default='Low') # Low, Medium, High
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_factor = db.Column(db.Float) # Contribution of attendance to risk
    academic_factor = db.Column(db.Float) # Contribution of grades to risk
