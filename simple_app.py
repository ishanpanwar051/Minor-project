from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduguard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='faculty')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_teacher(self):
        return self.role == 'faculty'
    
    def is_student(self):
        return self.role == 'student'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_student():
            return redirect(url_for('student_dashboard'))
        else:
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
            flash(f'Welcome back, {user.username}!', 'success')
            
            if user.is_student():
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_student():
        return redirect(url_for('student_dashboard'))
    
    # Get all users for admin
    if current_user.is_admin():
        users = User.query.all()
        return render_template('admin_dashboard.html', users=users)
    else:
        return render_template('teacher_dashboard.html')

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if not current_user.is_student():
        flash('Access denied. Student access required.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('student_dashboard.html')

# Create default users
def create_users():
    with app.app_context():
        db.create_all()
    
    # Create admin user
    if not User.query.filter_by(email='admin@eduguard.com').first():
        admin = User(username='admin', email='admin@eduguard.com', role='admin')
        admin.set_password('Admin123!')
        db.session.add(admin)
    
    # Create teacher user
    if not User.query.filter_by(email='teacher@eduguard.com').first():
        teacher = User(username='teacher', email='teacher@eduguard.com', role='faculty')
        teacher.set_password('Teacher123!')
        db.session.add(teacher)
    
    # Create student user
    if not User.query.filter_by(email='student@eduguard.com').first():
        student = User(username='student', email='student@eduguard.com', role='student')
        student.set_password('Student123!')
        db.session.add(student)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        create_users()
        
        print("Default users created:")
        print("Admin: admin@eduguard.com / Admin123!")
        print("Teacher: teacher@eduguard.com / Teacher123!")
        print("Student: student@eduguard.com / Student123!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
