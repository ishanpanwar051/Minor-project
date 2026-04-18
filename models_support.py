from models import db
from datetime import datetime, date

class StudentGoal(db.Model):
    __tablename__ = 'student_goals'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    progress = db.Column(db.Integer, default=0)  # 0-100 percent
    status = db.Column(db.String(20), default='Active')  # Active, Completed, Abandoned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    student = db.relationship('Student', backref='student_goals')
    
    def __repr__(self):
        return f'<StudentGoal {self.id}: {self.title}>'
    
    def is_overdue(self):
        if self.target_date and self.status == 'Active':
            return date.today() > self.target_date
        return False
    
    def days_remaining(self):
        if self.target_date and self.status == 'Active':
            delta = self.target_date - date.today()
            return delta.days
        return None

class MoodLog(db.Model):
    __tablename__ = 'mood_logs'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)  # 1=very bad, 2=bad, 3=neutral, 4=good, 5=great
    note = db.Column(db.Text)  # optional
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    log_date = db.Column(db.Date, default=date.today)
    
    # Relationship
    student = db.relationship('Student', backref='mood_logs')
    
    def __repr__(self):
        return f'<MoodLog {self.id}: Score {self.mood_score}>'
    
    def get_mood_color(self):
        colors = {
            1: 'danger',    # very bad - red
            2: 'warning',    # bad - orange
            3: 'secondary',  # neutral - gray
            4: 'info',       # good - light blue
            5: 'success'     # great - green
        }
        return colors.get(self.mood_score, 'secondary')
    
    def get_mood_text(self):
        texts = {
            1: 'Very Bad',
            2: 'Bad',
            3: 'Neutral',
            4: 'Good',
            5: 'Great'
        }
        return texts.get(self.mood_score, 'Unknown')
    
    def get_mood_emoji(self):
        emojis = {
            1: '😢',  # very bad
            2: '😔',  # bad
            3: '😐',  # neutral
            4: '😊',  # good
            5: '😄'   # great
        }
        return emojis.get(self.mood_score, '❓')
