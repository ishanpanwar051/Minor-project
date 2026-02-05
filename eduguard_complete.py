"""
EduGuard - Complete Working Application
Single file solution to avoid SQLAlchemy instance issues
"""

from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import hashlib
import os

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduguard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='faculty')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        try:
            return check_password_hash(self.password_hash, password)
        except:
            simple_hash = hashlib.sha256(password.encode()).hexdigest()
            return self.password_hash == simple_hash

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(50))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    enrollment_date = db.Column(db.Date)
    credits_completed = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref='student_profile')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login_standalone.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard_final.html')

@app.route('/students')
@login_required
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@app.route('/student/<int:id>')
@login_required
def student_detail(id):
    student = Student.query.get_or_404(id)
    return render_template('student_detail.html', student=student)

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        # Simple mock prediction
        prediction = {
            'student_id': student_id,
            'risk_score': 75.5,
            'risk_level': 'High',
            'recommendations': [
                'Improve attendance rate',
                'Focus on academic performance',
                'Seek counselling support'
            ]
        }
        return render_template('prediction_result.html', prediction=prediction)
    
    return render_template('predict.html')

# Initialize database and create admin user
def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@university.edu').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@university.edu',
                role='admin'
            )
            admin.password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            db.session.add(admin)
            
            # Create test student
            student_user = User(
                username='student001',
                email='john.doe@university.edu',
                role='student'
            )
            student_user.password_hash = hashlib.sha256('student123'.encode()).hexdigest()
            db.session.add(student_user)
            db.session.commit()
            
            student = Student(
                user_id=student_user.id,
                student_id='CS101',
                first_name='John',
                last_name='Doe',
                email='john.doe@university.edu',
                department='Computer Science',
                year=2,
                semester=1,
                gpa=3.5,
                enrollment_date=date(2022, 9, 1),
                credits_completed=60
            )
            db.session.add(student)
            db.session.commit()
            
            print("✅ Database initialized with admin user")
            print("🔐 Admin credentials: admin@university.edu / admin123")

if __name__ == '__main__':
    init_db()
    print("\n🚀 EduGuard Application Starting...")
    print("🌐 Access at: http://127.0.0.1:5000")
    print("🔐 Admin Login: admin@university.edu / admin123")
    print("👨‍🎓 Student Login: john.doe@university.edu / student123")
    app.run(debug=True, host='0.0.0.0', port=5000)
