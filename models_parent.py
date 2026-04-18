from models import db
from datetime import datetime

class ParentMessage(db.Model):
    __tablename__ = 'parent_messages'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    sender_role = db.Column(db.String(20), nullable=False)  # 'parent' or 'faculty'
    sender_name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    # Relationship
    student = db.relationship('Student', backref='parent_messages')
    
    def __repr__(self):
        return f'<ParentMessage {self.id} from {self.sender_role}>'
