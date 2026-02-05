"""
Security Log Model for EduGuard System
Tracks security events and user activities
"""

from datetime import datetime
from models import db

class SecurityLog(db.Model):
    __tablename__ = 'security_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50))  # login, logout, failed_login, form_submit, api_access, etc.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45))  # Client IP address
    user_agent = db.Column(db.Text)  # Browser user agent
    details = db.Column(db.Text)  # Additional details
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='security_logs')
    
    def __repr__(self):
        return f'<SecurityLog {self.id} - {self.event_type}>'

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(255))  # Flask session ID
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='sessions')
    
    def __repr__(self):
        return f'<UserSession {self.id}>'
