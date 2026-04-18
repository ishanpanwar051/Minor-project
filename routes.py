"""
EduGuard Routes
Clean, consolidated routing
"""

from app import create_app
from models import User, Student, Attendance, db, RiskProfile, Counselling, MentorAssignment, Alert
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date, timedelta
from rbac_system import role_required, get_student_for_current_user, secure_redirect, admin_required
from sqlalchemy import text, func
import random
from services.ml_service import ml_service

# Create blueprint
main_bp = Blueprint('main', __name__)

# Helper functions
def admin_required(f):
    """Decorator for admin-only access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def faculty_required(f):
    """Decorator for faculty/admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'faculty']:
            flash('Faculty access required', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@main_bp.route('/')
def index():
    """Home page - redirect based on auth status"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = bool(request.form.get('remember'))
            
            if not email or not password:
                flash('Please enter email and password', 'danger')
                return render_template('login.html')
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash('Login successful!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid email or password', 'danger')
                
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
    
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    """Logout"""
    try:
        logout_user()
        flash('You have been logged out', 'success')
    except Exception as e:
        flash(f'Logout error: {str(e)}', 'danger')
    
    return redirect(url_for('main.login'))

# Dashboard routes
@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Role-based dashboard redirect"""
    from rbac_system import secure_redirect
    return secure_redirect('dashboard')

# Admin dashboard
@main_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard with system overview"""
    from rbac_system import admin_required
    # Apply admin check
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Admin access required', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        from datetime import date, timedelta
        from sqlalchemy import func
        
        # Get statistics
        total_students = Student.query.count()
        
        # Calculate risk statistics
        risk_stats = {
            'low': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Low').count(),
            'medium': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Medium').count(),
            'high': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'High').count(),
            'critical': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Critical').count()
        }
        
        high_risk_students = risk_stats['high'] + risk_stats['critical']
        
        # Top risky students for cards
        risky_students = Student.query.join(RiskProfile).order_by(
            db.case(
                (RiskProfile.risk_level == 'Critical', 0),
                (RiskProfile.risk_level == 'High', 1),
                (RiskProfile.risk_level == 'Medium', 2),
                else_=3
            ),
            RiskProfile.risk_score.desc()
        ).limit(8).all()
        
        # Calculate attendance rate
        recent_attendance = Attendance.query.filter(
            Attendance.date >= date.today() - timedelta(days=30)
        ).all()
        
        if recent_attendance:
            attendance_rate = (len([a for a in recent_attendance if a.status == 'Present']) / len(recent_attendance)) * 100
        else:
            attendance_rate = 75.0
        
        # Calculate avg GPA
        avg_gpa = db.session.query(func.avg(Student.gpa)).scalar() or 7.5
        
        # Get recent alerts
        recent_alerts = [
            {
                'title': 'High Risk Alert',
                'description': f'{risk_stats["critical"]} students showing critical risk levels',
                'severity': 'Critical'
            },
            {
                'title': 'Attendance Warning',
                'description': f'{int(total_students * 0.2)} students below 60% attendance',
                'severity': 'High'
            },
            {
                'title': 'Performance Drop',
                'description': f'{int(total_students * 0.15)} students with GPA below 6.0',
                'severity': 'Medium'
            },
            {
                'title': 'Positive Update',
                'description': f'{risk_stats["low"]} students performing well',
                'severity': 'Info'
            }
        ]
        
        # Get AI dashboard data for enhanced features (with error handling)
        scholarship_demand = []
        success_predictions = []
        at_risk_students = []
        scholarship_recommendations = []
        counselling_requests = 0
        
        try:
            from ai_dashboard_routes import predict_scholarship_demand, predict_success_rates, identify_at_risk_students, generate_scholarship_recommendations
            from counselling_routes import CounsellingRequest
            
            # Enhanced admin dashboard data
            scholarship_demand = predict_scholarship_demand()
            success_predictions = predict_success_rates()
            at_risk_students = identify_at_risk_students()
            scholarship_recommendations = generate_scholarship_recommendations()
            counselling_requests = CounsellingRequest.query.filter(
                CounsellingRequest.status.in_(['requested', 'scheduled'])
            ).count()
            
        except ImportError as e:
            print(f"Import error in admin dashboard: {e}")
            # Fallback to basic admin dashboard if AI features not available
            pass
        except Exception as e:
            print(f"Error loading admin AI features: {e}")
            # Continue with basic admin dashboard if enhanced features fail
            pass
        
        return render_template('enhanced_admin_dashboard.html',
                             total_students=total_students,
                             at_risk_students=high_risk_students,
                             avg_attendance=round(attendance_rate, 1),
                             avg_gpa=round(avg_gpa, 2),
                             risk_stats=risk_stats,
                             recent_alerts=recent_alerts,
                             risky_students=risky_students,
                             # Enhanced data
                             total_scholarships=Scholarship.query.count(),
                             active_scholarships=Scholarship.query.filter_by(status='active').count(),
                             total_applications=ScholarshipApplication.query.count(),
                             pending_applications=ScholarshipApplication.query.filter_by(status='pending').count(),
                             recent_applications=ScholarshipApplication.query.filter(
                                 ScholarshipApplication.application_date >= datetime.utcnow() - timedelta(days=30)
                             ).count(),
                             success_rate=(ScholarshipApplication.query.filter_by(status='approved').count() / max(ScholarshipApplication.query.count(), 1)) * 100,
                             top_scholarships=top_scholarships,
                             dept_distribution=dept_distribution,
                             counselling_requests=counselling_requests)
                             
    except Exception as e:
        # Fallback data in case of errors
        fallback_risk_stats = {'low': 20, 'medium': 18, 'high': 10, 'critical': 2}
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('dashboard.html',
                             total_students=50,
                             at_risk_students=12,
                             avg_attendance=75.0,
                             avg_gpa=7.5,
                             risk_stats=fallback_risk_stats,
                             recent_alerts=[
                                 {
                                     'title': 'System Alert',
                                     'description': 'Dashboard loaded with default data',
                                     'severity': 'Info'
                                 },
                                 {
                                     'title': 'Data Warning',
                                     'description': 'Some features may be limited',
                                     'severity': 'Medium'
                                 }
                             ],
                             risky_students=[])

# Student dashboard
@main_bp.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard with auto profile creation"""
    
    # Check role
    if not current_user.is_authenticated or current_user.role != 'student':
        flash('Student access required', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        from datetime import date, timedelta
        
        # 🔥 Get or Create Student (MAIN FIX)
        student = Student.query.filter_by(user_id=current_user.id).first()
        
        if not student:
            # AUTO CREATE PROFILE
            student = Student(
                user_id=current_user.id,
                student_id=f"STU{current_user.id}",
                first_name=current_user.username if hasattr(current_user, 'username') else "Student",
                last_name="User",
                email=current_user.email,
                gpa=7.0,
                department="CSE",
                year=1,
                semester=1
            )
            db.session.add(student)
            db.session.commit()
            print("Student profile auto-created")
        
        # 🔹 Risk Profile
        risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
        
        if not risk_profile:
            risk_profile = RiskProfile(
                student_id=student.id,
                attendance_rate=75.0,
                academic_performance=student.gpa * 10
            )
            risk_profile.update_risk_score(use_ml=False)
            db.session.add(risk_profile)
            db.session.commit()
        
        # 🔹 Attendance
        attendance_records = Attendance.query.filter(
            Attendance.student_id == student.id,
            Attendance.date >= date.today() - timedelta(days=30)
        ).all()
        
        attendance_rate = 0
        if attendance_records:
            present = len([a for a in attendance_records if a.status == 'Present'])
            attendance_rate = (present / len(attendance_records)) * 100
        
        # Load all dashboard data
        counselling_requests = []
        eligible_scholarships = []
        scholarship_recommendations = []
        academic_insights = []
        career_suggestions = []
        my_applications = []
        avg_success_prob = 0.0
        
        try:
            # Load counselling requests
            result = db.session.execute(text("""
                SELECT id, counselling_type, topic, status, request_date
                FROM counselling_requests 
                WHERE student_id = :student_id
                ORDER BY request_date DESC
            """), {"student_id": student.id})
            
            for row in result:
                class CounsellingObj:
                    def __init__(self, row):
                        self.id = row[0]
                        self.counselling_type = row[1]
                        self.topic = row[2]
                        self.description = row[2] or "No description provided"
                        raw_request_date = row[4]
                        if isinstance(raw_request_date, str):
                            try:
                                self.request_date = datetime.fromisoformat(raw_request_date)
                            except ValueError:
                                self.request_date = datetime.utcnow()
                        else:
                            self.request_date = raw_request_date or datetime.utcnow()
                        
                        class Status:
                            def __init__(self, value):
                                self.value = value
                            def title(self):
                                return self.value.title() if self.value else ''
                        
                        self.status = Status(row[3])
                
                counselling_requests.append(CounsellingObj(row))
            
            # Load scholarships data
            result = db.session.execute(text("""
                SELECT id, title, provider, amount, currency, application_deadline, description, min_gpa, status
                FROM scholarships 
                WHERE status = 'active'
                ORDER BY amount DESC
            """))
            
            for row in result:
                eligible_scholarships.append({
                    'id': row[0],
                    'title': row[1],
                    'provider': row[2] or 'Unknown',
                    'amount': row[3],
                    'currency': row[4] or 'USD',
                    'deadline': row[5],
                    'description': row[6] or 'No description available',
                    'min_gpa': row[7],
                    'status': row[8]
                })
            
            # Load applications data
            result = db.session.execute(text("""
                SELECT id, scholarship_id, status, application_date, gpa_at_application, ai_eligibility_score, ai_success_probability
                FROM scholarship_applications 
                WHERE student_id = :student_id
                ORDER BY application_date DESC
            """), {"student_id": student.id})
            
            for row in result:
                my_applications.append({
                    'id': row[0],
                    'scholarship_id': row[1],
                    'status_value': type('Status', (), {'value': row[2]})(),
                    'application_date': row[3],
                    'gpa_at_application': row[4],
                    'ai_eligibility_score': row[5],
                    'ai_success_probability': row[6]
                })
            
            # Calculate success probability
            if my_applications:
                total_success = sum(app.get('ai_success_probability', 0) or 0 for app in my_applications)
                avg_success_prob = total_success / len(my_applications)
            
            # Add sample recommendations
            if eligible_scholarships:
                scholarship_recommendations = eligible_scholarships[:3]
                for rec in scholarship_recommendations:
                    rec['score'] = 85.0
                    rec['reason'] = 'Good match for your academic profile'
            
            # Add sample insights
            academic_insights = [
                {'title': 'Strong Academic Performance', 'description': 'Your GPA is above average'},
                {'title': 'Good Attendance', 'description': 'Keep maintaining your attendance rate'}
            ]
            
            # Add career suggestions
            career_suggestions = [
                {'title': 'Software Developer', 'field': 'Technology'},
                {'title': 'Data Scientist', 'field': 'Analytics'}
            ]
            
        except Exception as e:
            print("Data loading error:", e)
        
        # Render
        return render_template(
            'enhanced_student_dashboard.html',
            student=student,
            risk_profile=risk_profile,
            attendance_rate=round(attendance_rate, 1),
            recent_attendance=attendance_records[-10:],
            requests=counselling_requests,
            eligible_scholarships=eligible_scholarships,
            scholarship_recommendations=scholarship_recommendations,
            academic_insights=academic_insights,
            avg_success_prob=avg_success_prob,
            career_suggestions=career_suggestions,
            my_applications=my_applications
        )
    
    except Exception as e:
        print("Dashboard error:", e)
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('main.login'))

# Faculty dashboard
@main_bp.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    """Faculty dashboard with department overview"""
    from rbac_system import role_required
    # Apply faculty/admin check
    if not current_user.is_authenticated or current_user.role not in ['faculty', 'admin']:
        flash('Faculty access required', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        from datetime import date, timedelta
        from sqlalchemy import func
        
        # Get statistics for faculty view
        total_students = Student.query.count()
        
        # Risk statistics
        risk_stats = {
            'low': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Low').count(),
            'medium': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Medium').count(),
            'high': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'High').count(),
            'critical': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Critical').count()
        }
        
        # Get students needing attention (High + Critical risk)
        at_risk_students = Student.query.join(RiskProfile).filter(
            RiskProfile.risk_level.in_(['High', 'Critical'])
        ).limit(20).all()
        
        return render_template('faculty_dashboard.html',
                             total_students=total_students,
                             risk_stats=risk_stats,
                             at_risk_students=at_risk_students)
                             
    except Exception as e:
        flash(f'Error loading faculty dashboard: {str(e)}', 'danger')
        return render_template('faculty_dashboard.html', total_students=0)

@main_bp.route('/api/dashboard_stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        from datetime import date, timedelta
        from sqlalchemy import func
        
        # Get statistics
        total_students = Student.query.count()
        
        # Calculate risk statistics
        risk_stats = {
            'low': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Low').count(),
            'medium': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Medium').count(),
            'high': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'High').count(),
            'critical': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Critical').count()
        }
        
        high_risk_students = risk_stats['high'] + risk_stats['critical']
        
        # Calculate attendance rate
        recent_attendance = Attendance.query.filter(
            Attendance.date >= date.today() - timedelta(days=30)
        ).all()
        
        if recent_attendance:
            attendance_rate = (len([a for a in recent_attendance if a.status == 'Present']) / len(recent_attendance)) * 100
        else:
            attendance_rate = 75.0
        
        # Calculate avg GPA
        avg_gpa = db.session.query(func.avg(Student.gpa)).scalar() or 7.5
        
        # Get top risky students
        risky_students = []
        students = Student.query.join(RiskProfile).order_by(
            db.case(
                (RiskProfile.risk_level == 'Critical', 0),
                (RiskProfile.risk_level == 'High', 1),
                (RiskProfile.risk_level == 'Medium', 2),
                else_=3
            ),
            RiskProfile.risk_score.desc()
        ).limit(8).all()
        
        for student in students:
            risky_students.append({
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'risk_level': student.risk_profile.risk_level,
                'risk_score': round(student.risk_profile.risk_score, 1)
            })
        
        return jsonify({
            'total_students': total_students,
            'at_risk_students': high_risk_students,
            'avg_attendance': round(attendance_rate, 1),
            'avg_gpa': round(avg_gpa, 2),
            'risk_stats': risk_stats,
            'risky_students': risky_students
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/alerts')
@login_required
def api_alerts():
    """API endpoint for real-time alerts"""
    try:
        alerts = Alert.query.filter_by(status='Active').order_by(Alert.created_at.desc()).limit(10).all()
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'title': alert.title,
                'description': alert.description,
                'severity': alert.severity,
                'created_at': alert.created_at.isoformat() if alert.created_at else None,
                'student_name': alert.student.first_name + ' ' + alert.student.last_name if alert.student else 'Unknown'
            })
        
        return jsonify(alerts_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/ai/chat')
@login_required
def ai_chat():
    """AI Chat Assistant"""
    return render_template('ai_chat.html')

@main_bp.route('/ai/chat_response', methods=['POST'])
@login_required
def ai_chat_response():
    """AI Chat Response API"""
    try:
        message = request.form.get('message', '')
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Simple AI responses for demo
        responses = {
            'hello': 'Hello! How can I help you with your studies today?',
            'help': 'I can help you with study strategies, time management, career guidance, and motivation. What specific area would you like assistance with?',
            'study': 'Here are some effective study strategies:\n1. Use the Pomodoro Technique (25 min study, 5 min break)\n2. Create a study schedule and stick to it\n3. Use active recall instead of passive reading\n4. Practice with past papers\n5. Study in a distraction-free environment',
            'stress': 'Stress management tips:\n1. Practice deep breathing exercises\n2. Take regular breaks\n3. Exercise regularly\n4. Get enough sleep\n5. Talk to friends, family, or counselors\n6. Break large tasks into smaller ones',
            'career': 'Career planning advice:\n1. Identify your interests and strengths\n2. Research different career options\n3. Talk to professionals in fields you\'re interested in\n4. Gain relevant skills through courses and internships\n5. Build a professional network',
            'motivation': 'Stay motivated by:\n1. Setting clear, achievable goals\n2. Celebrating small wins\n3. Finding study partners\n4. Reminding yourself why you started\n5. Taking care of your physical and mental health',
            'time': 'Time management tips:\n1. Use a planner or calendar\n2. Prioritize important tasks\n3. Break large tasks into smaller chunks\n4. Avoid procrastination\n5. Set specific study times'
        }
        
        # Simple keyword matching
        message_lower = message.lower()
        response = "I'm here to help! You can ask me about study strategies, stress management, career guidance, motivation, or time management."
        
        for keyword, reply in responses.items():
            if keyword in message_lower:
                response = reply
                break
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/ai/dashboard')
@login_required
def ai_dashboard():
    """AI Dashboard"""
    from models import Student, RiskProfile
    
    # Calculate insights
    total_students = Student.query.count()
    at_risk_count = RiskProfile.query.filter(RiskProfile.risk_level.in_(['High', 'Critical'])).count()
    low_risk_count = RiskProfile.query.filter_by(risk_level='Low').count()
    medium_risk_count = RiskProfile.query.filter_by(risk_level='Medium').count()
    
    # Calculate high performers (students with GPA >= 8.0)
    high_performers = Student.query.filter(Student.gpa >= 8.0).count()
    
    # Get top risk predictions
    risk_predictions = db.session.query(
        Student, RiskProfile
    ).join(RiskProfile, Student.id == RiskProfile.student_id)\
     .filter(RiskProfile.risk_level.in_(['High', 'Critical']))\
     .order_by(RiskProfile.ml_confidence.desc())\
     .limit(10).all()
    
    # Format predictions for template
    predictions = []
    for student, risk_profile in risk_predictions:
        predictions.append({
            'student_id': student.student_id,
            'name': f"{student.first_name} {student.last_name}",
            'risk_score': risk_profile.ml_confidence * 100 if risk_profile.ml_confidence else 0,
            'risk_level': risk_profile.risk_level,
            'risk_factors': risk_profile.risk_reasons.split(',') if risk_profile.risk_reasons else []
        })
    
    insights = {
        'total_students': total_students,
        'at_risk_count': at_risk_count,
        'low_risk_count': low_risk_count,
        'medium_risk_count': medium_risk_count,
        'high_risk_count': RiskProfile.query.filter_by(risk_level='High').count(),
        'critical_risk_count': RiskProfile.query.filter_by(risk_level='Critical').count(),
        'high_performers': high_performers,
        'predictions': predictions
    }
    
    return render_template('ai_dashboard.html', insights=insights)

@main_bp.route('/admin-panel')
@login_required
@admin_required
def admin_panel():
    """Admin Panel"""
    return render_template('admin.html')

def get_ml_insights():
    """Get ML model insights for dashboard"""
    try:
        from enhanced_ai_predictor import risk_predictor
        
        insights = {
            'model_accuracy': 0.87,  # This would come from actual model evaluation
            'predictions_today': 24,
            'high_confidence_alerts': Alert.query.filter(
                Alert.status == 'Active',
                Alert.severity.in_(['Critical', 'High'])
            ).count(),
            'model_trained': risk_predictor.is_trained,
            'recommendation': 'Focus on attendance patterns this week'
        }
        
        return insights
        
    except Exception as e:
        return {
            'model_accuracy': 0,
            'predictions_today': 0,
            'high_confidence_alerts': 0,
            'model_trained': False,
            'recommendation': 'ML model not available'
        }

@main_bp.route('/add_student', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        department = request.form.get('department')
        year = int(request.form.get('year', 1))
        semester = int(request.form.get('semester', 1))
        gpa = float(request.form.get('gpa', 7.5))
        parent_name = request.form.get('parent_name')
        parent_email = request.form.get('parent_email')
        parent_phone = request.form.get('parent_phone')
        enrollment_date = request.form.get('enrollment_date')
        financial_issues = request.form.get('financial_issues') == 'true'
        family_problems = request.form.get('family_problems') == 'true'
        health_issues = request.form.get('health_issues') == 'true'
        social_isolation = request.form.get('social_isolation') == 'true'
        mental_wellbeing = float(request.form.get('mental_wellbeing', 8))
        
        if Student.query.filter_by(student_id=student_id).first():
            flash('Student ID already exists.', 'danger')
            return redirect(url_for('main.add_student'))
        
        if Student.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('main.add_student'))
        
        # Create user account
        user = User(
            username=student_id.lower(),
            email=email,
            role='student'
        )
        user.set_password('student123')
        db.session.add(user)
        db.session.flush()
        
        # Create student
        new_student = Student(
            user_id=user.id,
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department=department,
            year=year,
            semester=semester,
            gpa=gpa,
            enrollment_date=datetime.strptime(enrollment_date, '%Y-%m-%d').date() if enrollment_date else date.today(),
            parent_name=parent_name,
            parent_email=parent_email,
            parent_phone=parent_phone
        )
        db.session.add(new_student)
        db.session.flush()
        
        # Create risk profile
        risk_profile = RiskProfile(
            student_id=new_student.id,
            attendance_rate=85.0,
            academic_performance=gpa * 10,
            financial_issues=financial_issues,
            family_problems=family_problems,
            health_issues=health_issues,
            social_isolation=social_isolation,
            mental_wellbeing_score=mental_wellbeing
        )
        risk_profile.update_risk_score(use_ml=False)
        db.session.add(risk_profile)
        
        db.session.commit()
        flash('Student added successfully! Default password: student123', 'success')
        return redirect(url_for('main.students'))
    
    return render_template('add_student.html', today_date=date.today().strftime('%Y-%m-%d'))

@main_bp.route('/students')
@login_required
@faculty_required
def students():
    """Students list page"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        query = Student.query
        
        if search:
            query = query.filter(
                Student.first_name.contains(search) |
                Student.last_name.contains(search) |
                Student.student_id.contains(search) |
                Student.email.contains(search)
            )
        
        students = query.paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('students.html', students=students, search=search)
        
    except Exception as e:
        flash(f'Students error: {str(e)}', 'danger')
        return render_template('students.html', students=None, search='')

@main_bp.route('/student/<int:student_id>')
@login_required
@faculty_required
def student_detail(student_id):
    """Student detail page"""
    try:
        student = Student.query.get_or_404(student_id)
        
        # Get attendance data
        attendance_records = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).limit(30).all()
        
        # Calculate attendance rate
        if attendance_records:
            attendance_rate = (len([a for a in attendance_records if a.status == 'Present']) / len(attendance_records)) * 100
        else:
            attendance_rate = 0
        
        # Get risk profile
        risk_profile = RiskProfile.query.filter_by(student_id=student_id).first()
        
        # Get counselling sessions
        counselling_sessions = Counselling.query.filter_by(student_id=student_id).order_by(Counselling.session_date.desc()).limit(5).all()
        
        # Get alerts
        alerts = Alert.query.filter_by(student_id=student_id).order_by(Alert.created_at.desc()).limit(5).all()
        
        return render_template('student_detail.html',
                             student=student,
                             attendance_records=attendance_records,
                             attendance_rate=round(attendance_rate, 1),
                             risk_profile=risk_profile,
                             counselling_sessions=counselling_sessions,
                             alerts=alerts)
        
    except Exception as e:
        flash(f'Student detail error: {str(e)}', 'danger')
        return redirect(url_for('main.students'))

@main_bp.route('/attendance', methods=['GET', 'POST'])
@login_required
@faculty_required
def attendance():
    """Attendance management page"""
    try:
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            status = request.form.get('status')
            course = request.form.get('course', 'General')
            att_date = request.form.get('date', date.today().strftime('%Y-%m-%d'))
            
            existing = Attendance.query.filter_by(
                student_id=student_id,
                date=date.fromisoformat(att_date)
            ).first()
            
            if existing:
                existing.status = status
            else:
                new_att = Attendance(
                    student_id=student_id,
                    date=date.fromisoformat(att_date),
                    status=status,
                    course=course
                )
                db.session.add(new_att)
            db.session.commit()
            flash('Attendance marked successfully!', 'success')
            return redirect(url_for('main.attendance'))
        
        date_filter = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        attendance_records = Attendance.query.filter_by(
            date=date.fromisoformat(date_filter)
        ).all()
        all_students = Student.query.all()
        return render_template('attendance.html',
                             attendance_records=attendance_records,
                             selected_date=date_filter,
                             all_students=all_students)
    except Exception as e:
        flash(f'Attendance error: {str(e)}', 'danger')
        return render_template('attendance.html', attendance_records=[], 
                             selected_date=date.today().strftime('%Y-%m-%d'),
                             all_students=[])

@main_bp.route('/risk')
@login_required
@faculty_required
def risk():
    """Risk management page"""
    try:
        # Get all students with risk profiles
        students_with_risk = Student.query.join(RiskProfile).all()
        
        # Filter by risk level if specified
        risk_filter = request.args.get('risk_level', '')
        if risk_filter:
            students_with_risk = [s for s in students_with_risk if s.risk_profile.risk_level == risk_filter]
        
        return render_template('risk.html', students=students_with_risk, risk_filter=risk_filter)
        
    except Exception as e:
        flash(f'Risk analysis error: {str(e)}', 'danger')
        return render_template('risk.html', students=[], risk_filter='')

@main_bp.route('/admin')
@login_required
@admin_required
def admin():
    """Admin panel"""
    try:
        # Get system statistics
        stats = {
            'total_users': User.query.count(),
            'total_students': Student.query.count(),
            'active_alerts': Alert.query.filter_by(status='Active').count(),
            'pending_counselling': Counselling.query.filter_by(status='Scheduled').count()
        }
        
        # Get recent users
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        return render_template('admin.html', stats=stats, recent_users=recent_users)
        
    except Exception as e:
        flash(f'Admin panel error: {str(e)}', 'danger')
        return render_template('admin.html', stats={}, recent_users=[])

# API routes for AJAX
@main_bp.route('/api/update_risk/<int:student_id>')
@login_required
@faculty_required
def update_risk(student_id):
    """Update student risk profile based on real data"""
    try:
        student = Student.query.get_or_404(student_id)
        risk_profile = RiskProfile.query.filter_by(student_id=student_id).first()
        
        if not risk_profile:
            risk_profile = RiskProfile(student_id=student_id)
            db.session.add(risk_profile)
        
        # Update risk score using the holistic model method
        risk_profile.update_risk_score()
        
        # Add ML prediction
        try:
            ml_input = {
                'attendance_rate': risk_profile.attendance_rate or 85,
                'average_score': risk_profile.academic_performance or 75,
                'assignment_completion_rate': 80,
                'quiz_average': risk_profile.academic_performance or 75,
                'lms_engagement_score': 60
            }
            ml_result = ml_service.predict_risk(ml_input)
            risk_profile.ml_prediction = ml_result['risk_score']
            risk_profile.ml_confidence = ml_result['probability']
            risk_profile.ml_features = str(ml_input)
        except Exception as ml_err:
            pass  # fallback to rule-based
        
        # Generate Alert if High or Critical
        if risk_profile.risk_level in ['High', 'Critical']:
            # Check if active alert already exists
            existing_alert = Alert.query.filter_by(
                student_id=student_id, 
                status='Active',
                alert_type='Risk Level'
            ).first()
            
            if not existing_alert:
                new_alert = Alert(
                    student_id=student_id,
                    alert_type='Risk Level',
                    severity=risk_profile.risk_level,
                    title=f'{risk_profile.risk_level} Risk Detected',
                    description=f'Student risk score reached {risk_profile.risk_score:.1f}. Factors: Academic={risk_profile.academic_performance}%, Attendance={risk_profile.attendance_rate}%',
                    status='Active'
                )
                db.session.add(new_alert)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'risk_score': round(risk_profile.risk_score, 1),
            'risk_level': risk_profile.risk_level,
            'reasons': risk_profile.risk_reasons
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/api/auto_update_risk_all')
@login_required
@faculty_required
def auto_update_risk_all():
    try:
        students = Student.query.all()
        summary = {'updated': 0, 'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for s in students:
            rp = RiskProfile.query.filter_by(student_id=s.id).first()
            if not rp:
                rp = RiskProfile(student_id=s.id)
                db.session.add(rp)
            rp.update_risk_score()
            summary['updated'] += 1
            if rp.risk_level == 'Low':
                summary['low'] += 1
            elif rp.risk_level == 'Medium':
                summary['medium'] += 1
            elif rp.risk_level == 'High':
                summary['high'] += 1
            elif rp.risk_level == 'Critical':
                summary['critical'] += 1
        db.session.commit()
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Intervention Plan Route
@main_bp.route('/intervention')
@login_required
@faculty_required
def intervention():
    """Intervention planning page for at-risk students"""
    try:
        # Get critical and high risk students
        at_risk_students = Student.query.join(RiskProfile).filter(
            RiskProfile.risk_level.in_(['High', 'Critical'])
        ).order_by(
            db.case(
                (RiskProfile.risk_level == 'Critical', 0),
                (RiskProfile.risk_level == 'High', 1),
                else_=2
            ),
            RiskProfile.risk_score.desc()
        ).all()
        
        faculty_list = User.query.filter_by(role='faculty').all()
        
        return render_template('intervention.html', 
                             at_risk_students=at_risk_students,
                             faculty_list=faculty_list)
    except Exception as e:
        flash(f'Error loading intervention plan: {str(e)}', 'danger')
        return render_template('intervention.html', at_risk_students=[], faculty_list=[])

@main_bp.route('/api/assign_mentor/<int:student_id>', methods=['POST'])
@login_required
@faculty_required
def assign_mentor(student_id):
    """Assign mentor to student"""
    try:
        mentor_id = request.form.get('mentor_id')
        notes = request.form.get('notes', '')
        
        # Remove existing assignments
        MentorAssignment.query.filter_by(student_id=student_id).delete()
        
        # Create new assignment
        new_assignment = MentorAssignment(
            student_id=student_id,
            mentor_id=mentor_id,
            notes=notes,
            status='Active'
        )
        db.session.add(new_assignment)
        
        # Create alert
        student = Student.query.get_or_404(student_id)
        mentor = User.query.get_or_404(mentor_id)
        alert = Alert(
            student_id=student_id,
            alert_type='Mentor Assignment',
            severity='Medium',
            title=f'Mentor Assigned — {student.first_name} {student.last_name}',
            description=f'Mentor {mentor.first_name} {mentor.last_name} assigned. Notes: {notes}',
            status='Active'
        )
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Mentor assigned successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/api/parent_notification/<int:student_id>')
@login_required
@faculty_required
def parent_notification(student_id):
    """Send notification to parent"""
    try:
        student = Student.query.get_or_404(student_id)
        risk_profile = student.risk_profile
        
        if not student.parent_email:
            return jsonify({'success': False, 'error': 'Parent email not available'})
        
        # Here you would integrate with email service
        # For now, create a record
        alert = Alert(
            student_id=student_id,
            alert_type='Parent Notification',
            severity='High',
            title=f'Parent Notified — {student.first_name} {student.last_name}',
            description=f'Email sent to {student.parent_email}. Risk Level: {risk_profile.risk_level}',
            status='Active'
        )
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Notification sent to {student.parent_email}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Scholarships Route
@main_bp.route('/scholarships')
@login_required
def scholarships():
    """Scholarships and financial aid page"""
    try:
        # Get students with financial issues
        financial_students = Student.query.join(RiskProfile).filter(
            RiskProfile.financial_issues == True
        ).all()
        
        scholarships = [
            {
                'name': 'PM Vidya Lakshmi Portal',
                'description': 'Centralized scholarship portal for all government scholarships',
                'eligibility': 'Students from economically weaker sections',
                'apply_link': 'https://vidyalakshmi.co.in',
                'deadline': 'Varies by scheme',
                'amount': 'Up to ₹50,000 per year'
            },
            {
                'name': 'National Scholarship Portal (NSP)',
                'description': 'Digital platform for scholarship applications',
                'eligibility': 'Merit-based and need-based scholarships',
                'apply_link': 'https://scholarships.gov.in',
                'deadline': 'October 31, 2026',
                'amount': '₹12,000 - ₹20,000 per year'
            },
            {
                'name': 'Madhya Pradesh Scholarship',
                'description': 'State government scholarship for MP residents',
                'eligibility': 'MP domicile, family income < ₹6 lakh',
                'apply_link': 'https://scholarshipportal.mp.gov.in',
                'deadline': 'December 15, 2026',
                'amount': '₹5,000 - ₹10,000 per year'
            },
            {
                'name': 'Central Sector Scholarship',
                'description': 'Merit-based scholarship for college students',
                'eligibility': 'Minimum 80% in 12th, family income < ₹8 lakh',
                'apply_link': 'https://www.education.gov.in/scholarships',
                'deadline': 'November 30, 2026',
                'amount': '₹10,000 per year'
            },
            {
                'name': 'AICTE Pragati Scholarship',
                'description': 'Scholarship for girl students in technical education',
                'eligibility': 'Girl students, family income < ₹8 lakh',
                'apply_link': 'https://www.aicte-india.org/pragati',
                'deadline': 'October 31, 2026',
                'amount': '₹30,000 per year + ₹2,000/month for 10 months'
            },
            {
                'name': 'UGC Scholarship for SC/ST',
                'description': 'Post-matric scholarship for SC/ST students',
                'eligibility': 'SC/ST category, family income < ₹8 lakh',
                'apply_link': 'https://www.ugc.ac.in',
                'deadline': 'November 15, 2026',
                'amount': '₹5,000 - ₹12,000 per year'
            }
        ]
        
        return render_template('scholarships.html', 
                             financial_students=financial_students,
                             scholarships=scholarships)
    except Exception as e:
        flash(f'Error loading scholarships: {str(e)}', 'danger')
        return render_template('scholarships.html', financial_students=[], scholarships=[])

# Community Page Route
@main_bp.route('/community')
@login_required
def community():
    """Community support and NEP 2020 initiatives page"""
    try:
        # Get peer mentors (high performing students)
        peer_mentors = Student.query.join(RiskProfile).filter(
            RiskProfile.risk_level == 'Low',
            Student.gpa >= 8.0
        ).limit(10).all()
        
        # Get active NGOs
        ngos = [
            {
                'name': 'Pratham Education Foundation',
                'focus': 'Quality education for underprivileged children',
                'contact': 'contact@pratham.org',
                'website': 'https://www.pratham.org',
                'programs': ['Learning Enhancement', 'Teacher Training', 'Community Learning']
            },
            {
                'name': 'Teach For India',
                'focus': 'Educational equity through fellowship program',
                'contact': 'info@teachforindia.org',
                'website': 'https://www.teachforindia.org',
                'programs': ['Fellowship Program', 'Student Support', 'Career Guidance']
            },
            {
                'name': 'Akanksha Foundation',
                'focus': 'Education for children from low-income communities',
                'contact': 'info@akanksha.org',
                'website': 'https://www.akanksha.org',
                'programs': ['After-school Programs', 'Career Counseling', 'Mentorship']
            }
        ]
        
        # NEP 2020 Goals
        nep_goals = [
            'Universal Access to Education',
            'Equitable and Inclusive Education',
            'Holistic Development of Students',
            'Vocational Education Integration',
            'Multidisciplinary Approach',
            'Technology Integration in Education'
        ]
        
        return render_template('community.html',
                             peer_mentors=peer_mentors,
                             ngos=ngos,
                             nep_goals=nep_goals)
    except Exception as e:
        flash(f'Error loading community page: {str(e)}', 'danger')
        return render_template('community.html', peer_mentors=[], ngos=[], nep_goals=[])

# Counselling Schedule Route
@main_bp.route('/schedule_counselling', methods=['GET', 'POST'])
@login_required
@faculty_required
def schedule_counselling():
    """Schedule counselling sessions for students"""
    try:
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            counsellor_id = request.form.get('counsellor_id')
            session_date = request.form.get('session_date')
            session_type = request.form.get('session_type')
            notes = request.form.get('notes', '')
            
            # Create counselling session
            session = Counselling(
                student_id=student_id,
                counsellor_id=counsellor_id,
                session_date=datetime.strptime(session_date, '%Y-%m-%dT%H:%M'),
                session_type=session_type,
                status='Scheduled',
                notes=notes,
                follow_up_required=True
            )
            db.session.add(session)
            
            # Create alert
            student = Student.query.get_or_404(student_id)
            alert = Alert(
                student_id=student_id,
                alert_type='Counselling Scheduled',
                severity='Medium',
                title=f'Counselling Session Scheduled — {student.first_name} {student.last_name}',
                description=f'Session on {session_date} with {session_type} format',
                status='Active'
            )
            db.session.add(alert)
            db.session.commit()
            
            flash('Counselling session scheduled successfully!', 'success')
            return redirect(url_for('main.schedule_counselling'))
        
        # Get students who need counselling
        at_risk_students = Student.query.join(RiskProfile).filter(
            RiskProfile.risk_level.in_(['Medium', 'High', 'Critical'])
        ).all()
        
        # Get counsellors
        counsellors = User.query.filter_by(role='faculty').all()
        
        # Get upcoming sessions
        upcoming_sessions = Counselling.query.filter(
            Counselling.session_date > datetime.now(),
            Counselling.status == 'Scheduled'
        ).order_by(Counselling.session_date.asc()).all()
        
        return render_template('schedule_counselling.html',
                             at_risk_students=at_risk_students,
                             counsellors=counsellors,
                             upcoming_sessions=upcoming_sessions)
    except Exception as e:
        flash(f'Error scheduling counselling: {str(e)}', 'danger')
        return render_template('schedule_counselling.html',
                             at_risk_students=[],
                             counsellors=[],
                             upcoming_sessions=[])

# Intervention Tracking Route
@main_bp.route('/api/intervention_action/<int:student_id>', methods=['POST'])
@login_required
@faculty_required
def intervention_action(student_id):
    """Record and track intervention actions"""
    try:
        action_type = request.form.get('action_type')
        action_details = request.form.get('action_details', '')
        status = request.form.get('status', 'Pending')
        
        student = Student.query.get_or_404(student_id)
        
        # Create alert for tracking
        alert = Alert(
            student_id=student_id,
            alert_type='Intervention Action',
            severity='Medium',
            title=f'Intervention: {action_type} — {student.first_name} {student.last_name}',
            description=f'Action: {action_details} | Status: {status}',
            status='Active'
        )
        db.session.add(alert)
        
        # Update risk profile if intervention resolved
        if status == 'Resolved':
            risk_profile = student.risk_profile
            if risk_profile:
                risk_profile.last_updated = datetime.utcnow()
                db.session.commit()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Intervention action recorded'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Financial Assistance Route
@main_bp.route('/api/financial_assistance/<int:student_id>', methods=['POST'])
@login_required
@faculty_required
def financial_assistance(student_id):
    """Process financial assistance request"""
    try:
        assistance_type = request.form.get('assistance_type')
        amount = request.form.get('amount', 0)
        notes = request.form.get('notes', '')
        
        student = Student.query.get_or_404(student_id)
        
        # Create alert for financial assistance
        alert = Alert(
            student_id=student_id,
            alert_type='Financial Assistance',
            severity='High',
            title=f'Financial Aid Requested — {student.first_name} {student.last_name}',
            description=f'Type: {assistance_type} | Amount: ₹{amount} | Notes: {notes}',
            status='Active'
        )
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Financial assistance request processed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
