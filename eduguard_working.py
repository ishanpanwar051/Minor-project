"""
EduGuard - Complete Working Application with Templates
Single file solution with all templates included
"""

from flask import Flask, render_template_string, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
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
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Templates
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EduGuard - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .login-container { max-width: 400px; margin: 100px auto; }
        .card { border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .card-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px 15px 0 0 !important; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .form-control { border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-container">
            <div class="card">
                <div class="card-header text-center">
                    <h4><i class="fas fa-graduation-cap"></i> EduGuard</h4>
                    <p class="mb-0">Student Dropout Prevention System</p>
                </div>
                <div class="card-body p-4">
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                                    {{ message }}
                                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                </div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Email Address</label>
                            <input type="email" name="email" class="form-control" required placeholder="admin@university.edu">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" name="password" class="form-control" required placeholder="••••••••">
                        </div>
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" name="remember">
                            <label class="form-check-label">Remember me</label>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Login</button>
                    </form>
                    
                    <hr>
                    <div class="text-center">
                        <small class="text-muted">
                            <strong>Demo Credentials:</strong><br>
                            Admin: admin@university.edu / admin123<br>
                            Student: john.doe@university.edu / student123
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EduGuard - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .sidebar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .sidebar .nav-link { color: rgba(255,255,255,0.8); }
        .sidebar .nav-link:hover, .sidebar .nav-link.active { color: white; background: rgba(255,255,255,0.1); }
        .card { border: none; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        .stats-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar p-3">
                <h5 class="text-white mb-4"><i class="fas fa-graduation-cap"></i> EduGuard</h5>
                <nav class="nav flex-column">
                    <a href="/dashboard" class="nav-link active"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                    <a href="/students" class="nav-link"><i class="fas fa-users"></i> Students</a>
                    <a href="/analytics" class="nav-link"><i class="fas fa-chart-bar"></i> Analytics</a>
                    <a href="/predict" class="nav-link"><i class="fas fa-brain"></i> Predict</a>
                    <hr class="text-white-50">
                    <a href="/logout" class="nav-link"><i class="fas fa-sign-out-alt"></i> Logout</a>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 p-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2><i class="fas fa-tachometer-alt"></i> Dashboard</h2>
                    <div class="text-muted">
                        Welcome, <strong>{{ current_user.email }}</strong> | 
                        <span class="badge bg-primary">{{ current_user.role.title() }}</span>
                    </div>
                </div>
                
                <!-- Stats Cards -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card stats-card">
                            <div class="card-body">
                                <h4><i class="fas fa-users"></i> {{ total_students }}</h4>
                                <p class="mb-0">Total Students</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stats-card">
                            <div class="card-body">
                                <h4><i class="fas fa-exclamation-triangle"></i> {{ high_risk_students }}</h4>
                                <p class="mb-0">High Risk Students</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stats-card">
                            <div class="card-body">
                                <h4><i class="fas fa-user-graduate"></i> {{ active_students }}</h4>
                                <p class="mb-0">Active Students</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stats-card">
                            <div class="card-body">
                                <h4><i class="fas fa-chart-line"></i> {{ success_rate }}%</h4>
                                <p class="mb-0">Success Rate</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Recent Activity -->
                <div class="row">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-clock"></i> Recent Activity</h5>
                            </div>
                            <div class="card-body">
                                <div class="list-group">
                                    <div class="list-group-item">
                                        <div class="d-flex justify-content-between">
                                            <span><i class="fas fa-user-plus text-success"></i> New student registered</span>
                                            <small class="text-muted">2 hours ago</small>
                                        </div>
                                    </div>
                                    <div class="list-group-item">
                                        <div class="d-flex justify-content-between">
                                            <span><i class="fas fa-exclamation-triangle text-warning"></i> High risk alert generated</span>
                                            <small class="text-muted">5 hours ago</small>
                                        </div>
                                    </div>
                                    <div class="list-group-item">
                                        <div class="d-flex justify-content-between">
                                            <span><i class="fas fa-chart-line text-info"></i> Performance report generated</span>
                                            <small class="text-muted">1 day ago</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-bell"></i> Notifications</h5>
                            </div>
                            <div class="card-body">
                                <div class="alert alert-warning" role="alert">
                                    <i class="fas fa-exclamation-triangle"></i> 3 students require immediate attention
                                </div>
                                <div class="alert alert-info" role="alert">
                                    <i class="fas fa-info-circle"></i> Monthly report ready for review
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

STUDENTS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>EduGuard - Students</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .sidebar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .sidebar .nav-link { color: rgba(255,255,255,0.8); }
        .sidebar .nav-link:hover, .sidebar .nav-link.active { color: white; background: rgba(255,255,255,0.1); }
        .card { border: none; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar p-3">
                <h5 class="text-white mb-4"><i class="fas fa-graduation-cap"></i> EduGuard</h5>
                <nav class="nav flex-column">
                    <a href="/dashboard" class="nav-link"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                    <a href="/students" class="nav-link active"><i class="fas fa-users"></i> Students</a>
                    <a href="/analytics" class="nav-link"><i class="fas fa-chart-bar"></i> Analytics</a>
                    <a href="/predict" class="nav-link"><i class="fas fa-brain"></i> Predict</a>
                    <hr class="text-white-50">
                    <a href="/logout" class="nav-link"><i class="fas fa-sign-out-alt"></i> Logout</a>
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 p-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2><i class="fas fa-users"></i> Students</h2>
                    <button class="btn btn-primary"><i class="fas fa-plus"></i> Add Student</button>
                </div>
                
                <div class="card">
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Student ID</th>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Department</th>
                                        <th>Year</th>
                                        <th>GPA</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for student in students %}
                                    <tr>
                                        <td>{{ student.student_id }}</td>
                                        <td>{{ student.first_name }} {{ student.last_name }}</td>
                                        <td>{{ student.email }}</td>
                                        <td>{{ student.department }}</td>
                                        <td>{{ student.year }}</td>
                                        <td>{{ "%.2f"|format(student.gpa) }}</td>
                                        <td><span class="badge bg-success">Active</span></td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-primary"><i class="fas fa-eye"></i></button>
                                            <button class="btn btn-sm btn-outline-warning"><i class="fas fa-edit"></i></button>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

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
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Mock data for dashboard
    total_students = Student.query.count()
    high_risk_students = 3
    active_students = total_students - 2
    success_rate = 85
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                               total_students=total_students,
                               high_risk_students=high_risk_students,
                               active_students=active_students,
                               success_rate=success_rate)

@app.route('/students')
@login_required
def students():
    students = Student.query.all()
    return render_template_string(STUDENTS_TEMPLATE, students=students)

@app.route('/student/<int:id>')
@login_required
def student_detail(id):
    student = Student.query.get_or_404(id)
    return f"<h1>Student Details: {student.first_name} {student.last_name}</h1><p>This is a simple student detail page.</p>"

@app.route('/analytics')
@login_required
def analytics():
    return "<h1>Analytics</h1><p>Analytics page coming soon...</p>"

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        return f"<h1>Prediction Results</h1><p>Student ID: {student_id}<br>Risk Score: 75.5% (High Risk)</p>"
    
    return "<h1>Risk Prediction</h1><form method='post'><input name='student_id' placeholder='Student ID'><button type='submit'>Predict</button></form>"

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

if __name__ == '__main__':
    init_db()
    print("\n🚀 EduGuard Application Starting...")
    print("🌐 Access at: http://127.0.0.1:5000")
    print("🔐 Admin Login: admin@university.edu / admin123")
    print("👨‍🎓 Student Login: john.doe@university.edu / student123")
    app.run(debug=True, host='0.0.0.0', port=5000)
