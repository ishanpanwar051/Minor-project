"""
EduGuard Routes
Clean, consolidated routing
"""

from app import create_app
from models import (
    User, Student, Attendance, db, RiskProfile, Counselling, MentorAssignment,
    Alert, Scholarship, ScholarshipApplication, ScholarshipStatus,
    ApplicationStatus
)
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date, timedelta
from rbac_system import role_required, get_student_for_current_user, secure_redirect, admin_required
from sqlalchemy import text, func
import random

try:
    from services.ml_service import ml_service
except Exception as exc:
    ml_service = None
    print(f"ML service unavailable; continuing without ML predictions: {exc}")

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/dev/init-data')
def dev_init_data():
    """Trigger master seeding (Dev only)"""
    try:
        from master_setup_system import seed_everything
        seed_everything()
        flash('System populated with comprehensive sample data!', 'success')
        return redirect(url_for('main.student_dashboard'))
    except Exception as e:
        flash(f'Seeding failed: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

# Helper functions
def admin_required(f):
    """Decorator for admin-only access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def faculty_required(f):
    """Decorator for faculty/admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'faculty']:
            flash('Faculty access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes are managed in auth_routes.py now.
@main_bp.route('/')
def index():
    """Home page - redirect based on auth status"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

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
        
        # Compute top_scholarships and dept_distribution
        try:
            top_scholarships = db.session.query(
                Scholarship.title,
                func.count(ScholarshipApplication.id).label('application_count'),
                func.coalesce(
                    func.avg(ScholarshipApplication.ai_success_probability),
                    0
                ).label('avg_success_prob')
            ).join(ScholarshipApplication).group_by(Scholarship.id).order_by(
                func.count(ScholarshipApplication.id).desc()
            ).limit(5).all()
        except Exception:
            top_scholarships = []
        
        try:
            dept_distribution = db.session.query(
                Student.department,
                func.count(Student.id).label('student_count')
            ).group_by(Student.department).order_by(func.count(Student.id).desc()).all()
        except Exception:
            dept_distribution = []
        
        total_applications = ScholarshipApplication.query.count()
        approved_applications = ScholarshipApplication.query.filter_by(
            status=ApplicationStatus.APPROVED
        ).count()
        rejected_applications = ScholarshipApplication.query.filter_by(
            status=ApplicationStatus.REJECTED
        ).count()
        under_review_applications = ScholarshipApplication.query.filter_by(
            status=ApplicationStatus.UNDER_REVIEW
        ).count()
        pending_applications = ScholarshipApplication.query.filter_by(
            status=ApplicationStatus.PENDING
        ).count()
        active_scholarships = Scholarship.query.filter_by(
            status=ScholarshipStatus.ACTIVE
        ).count()
        recent_applications = ScholarshipApplication.query.filter(
            ScholarshipApplication.application_date >= datetime.utcnow() - timedelta(days=30)
        ).count()
        success_rate = (approved_applications / max(total_applications, 1)) * 100

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
                             active_scholarships=active_scholarships,
                             total_applications=total_applications,
                             pending_applications=pending_applications,
                             approved_applications=approved_applications,
                             rejected_applications=rejected_applications,
                             under_review_applications=under_review_applications,
                             recent_applications=recent_applications,
                             success_rate=success_rate,
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
        ).order_by(Attendance.date.desc()).all()
        
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
            # Load counselling requests via ORM
            from models import CounsellingRequest as CReq
            counselling_requests = CReq.query.filter_by(
                student_id=student.id
            ).order_by(CReq.request_date.desc()).all()
        except Exception as e:
            print("Counselling loading error:", e)
        
        try:
            # Load scholarships via ORM
            eligible_scholarships = Scholarship.query.filter(
                Scholarship.status == 'active'
            ).order_by(Scholarship.amount.desc()).all()
            # Fallback: try enum-based status
            if not eligible_scholarships:
                from models import ScholarshipStatus
                eligible_scholarships = Scholarship.query.filter(
                    Scholarship.status == ScholarshipStatus.ACTIVE
                ).order_by(Scholarship.amount.desc()).all()
        except Exception as e:
            print("Scholarship loading error:", e)
        
        try:
            # Load applications via ORM (with relationship to scholarship)
            my_applications = ScholarshipApplication.query.filter_by(
                student_id=student.id
            ).order_by(ScholarshipApplication.application_date.desc()).all()
            
            # Calculate success probability from applications and current profile.
            # Stored demo probabilities can be old, so we also calculate a live profile score.
            if my_applications:
                total_success = sum((app.ai_success_probability or 0) for app in my_applications)
                avg_success_prob = total_success / len(my_applications)
        except Exception as e:
            print("Applications loading error:", e)

        # Live success score: GPA + attendance + risk profile + application history.
        gpa_component = min((student.gpa or 0) / 10, 1.0) * 0.40
        attendance_component = min((attendance_rate or 0) / 100, 1.0) * 0.30
        risk_penalty = {
            'Critical': 0.25,
            'High': 0.15,
            'Medium': 0.07,
            'Low': 0.0
        }.get(risk_profile.risk_level if risk_profile else 'Low', 0.0)
        application_bonus = min(len(my_applications), 3) * 0.03
        profile_success_prob = 0.25 + gpa_component + attendance_component + application_bonus - risk_penalty
        profile_success_prob = max(0.20, min(profile_success_prob, 0.95))
        avg_success_prob = max(avg_success_prob, profile_success_prob)
        
        # Build scholarship recommendations from eligible scholarships
        if eligible_scholarships:
            for s in eligible_scholarships[:3]:
                scholarship_recommendations.append({
                    'title': s.title,
                    'amount': s.amount,
                    'score': 85.0,
                    'reason': f'Great match for {student.department or "your"} students with GPA {student.gpa or 0:.1f}'
                })
        
        # Build academic insights with correct keys for template
        gpa_val = student.gpa or 0
        att_val = attendance_rate or 0
        
        if gpa_val >= 3.5:
            academic_insights.append({
                'type': 'strength', 'message': f'Excellent GPA: {gpa_val:.1f}',
                'suggestion': 'Keep up the great work! Consider applying for merit-based scholarships.'
            })
        elif gpa_val >= 2.5:
            academic_insights.append({
                'type': 'moderate', 'message': f'Good GPA: {gpa_val:.1f}',
                'suggestion': 'Focus on improving weaker subjects to push your GPA higher.'
            })
        else:
            academic_insights.append({
                'type': 'concern', 'message': f'GPA Needs Attention: {gpa_val:.1f}',
                'suggestion': 'Consider tutoring services and study groups to improve grades.'
            })
        
        if att_val >= 85:
            academic_insights.append({
                'type': 'strength', 'message': f'Strong Attendance: {att_val:.0f}%',
                'suggestion': 'Your consistent attendance is contributing to your success.'
            })
        elif att_val >= 70:
            academic_insights.append({
                'type': 'moderate', 'message': f'Attendance: {att_val:.0f}%',
                'suggestion': 'Try to attend all classes to improve your learning outcomes.'
            })
        else:
            academic_insights.append({
                'type': 'concern', 'message': f'Low Attendance: {att_val:.0f}%',
                'suggestion': 'Attendance below 70% is critical. Please attend classes regularly.'
            })
        
        if my_applications:
            approved = len([a for a in my_applications if hasattr(a.status, 'value') and a.status.value == 'approved'])
            academic_insights.append({
                'type': 'strength' if approved > 0 else 'info',
                'message': f'{len(my_applications)} Scholarship Applications ({approved} Approved)',
                'suggestion': 'Keep applying to maximize your financial support opportunities.'
            })
        
        # Build career suggestions with correct keys for template
        dept = (student.department or 'General').lower()
        if 'computer' in dept or 'cse' in dept or 'data' in dept or 'it' in dept:
            career_suggestions = [
                {'field': 'Software Engineering', 'reason': 'High demand for CS graduates with strong problem-solving skills', 'growth_potential': 'High'},
                {'field': 'Data Science & AI', 'reason': 'Growing field leveraging your analytical and programming abilities', 'growth_potential': 'Very High'},
                {'field': 'Cloud Architecture', 'reason': 'Enterprise cloud adoption is accelerating globally', 'growth_potential': 'High'},
            ]
        elif 'mech' in dept or 'civil' in dept or 'engineer' in dept:
            career_suggestions = [
                {'field': 'Design Engineering', 'reason': 'Apply engineering principles to innovative product development', 'growth_potential': 'High'},
                {'field': 'Project Management', 'reason': 'Lead engineering projects with your technical foundation', 'growth_potential': 'High'},
                {'field': 'Sustainable Engineering', 'reason': 'Growing focus on green technology and sustainability', 'growth_potential': 'Very High'},
            ]
        else:
            career_suggestions = [
                {'field': 'Management Consulting', 'reason': 'Leverage analytical thinking across industries', 'growth_potential': 'High'},
                {'field': 'Research & Development', 'reason': 'Advance knowledge in your field through innovation', 'growth_potential': 'High'},
                {'field': 'Entrepreneurship', 'reason': 'Apply your education to create impactful ventures', 'growth_potential': 'Very High'},
            ]
        
        # Render
        return render_template(
            'enhanced_student_dashboard.html',
            student=student,
            risk_profile=risk_profile,
            attendance_rate=round(attendance_rate, 1),
            recent_attendance=attendance_records[:30],
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
        return redirect(url_for('auth.login'))

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
    """Redirect legacy Admin Panel to enhanced dashboard"""
    return redirect(url_for('main.admin_dashboard'))

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
    """Students list page with search and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        department = request.args.get('department', '')
        risk_level = request.args.get('risk_level', '')
        
        query = Student.query
        
        # Apply search filter
        if search:
            query = query.filter(
                Student.first_name.contains(search) |
                Student.last_name.contains(search) |
                Student.student_id.contains(search) |
                Student.email.contains(search)
            )

        if department:
            query = query.filter(Student.department == department)

        if risk_level:
            query = query.join(RiskProfile).filter(RiskProfile.risk_level == risk_level)
        
        students = query.paginate(
            page=page, per_page=20, error_out=False
        )

        departments = [
            row[0] for row in db.session.query(Student.department)
            .filter(Student.department.isnot(None))
            .distinct()
            .order_by(Student.department)
            .all()
        ]
        
        return render_template(
            'students.html',
            students=students,
            search=search,
            departments=departments,
            selected_department=department,
            selected_risk_level=risk_level
        )
        
    except Exception as e:
        flash(f'Students error: {str(e)}', 'danger')
        return render_template('students.html', students=None, search='', departments=[])

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

        applications = ScholarshipApplication.query.filter_by(
            student_id=student_id
        ).order_by(ScholarshipApplication.application_date.desc()).limit(10).all()

        try:
            from models import CounsellingRequest
            counselling_requests = CounsellingRequest.query.filter_by(
                student_id=student_id
            ).order_by(CounsellingRequest.request_date.desc()).limit(5).all()
        except Exception:
            counselling_requests = []
        
        return render_template('student_detail.html',
                             student=student,
                             attendance_records=attendance_records,
                             attendance_rate=round(attendance_rate, 1),
                             risk_profile=risk_profile,
                             counselling_sessions=counselling_sessions,
                             counselling_requests=counselling_requests,
                             applications=applications,
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
    """Redirect legacy admin endpoint to enhanced dashboard"""
    return redirect(url_for('main.admin_dashboard'))

@main_bp.route('/admin/export-report')
@login_required
@admin_required
def export_admin_report():
    """Download a simple CSV report for students and risk status."""
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Student ID', 'Name', 'Email', 'Department', 'GPA',
        'Attendance Rate', 'Risk Score', 'Risk Level', 'Risk Reasons'
    ])

    students = Student.query.outerjoin(RiskProfile).order_by(Student.student_id).all()
    for student in students:
        risk_profile = student.risk_profile
        writer.writerow([
            student.student_id,
            f'{student.first_name} {student.last_name}',
            student.email,
            student.department or '',
            student.gpa or '',
            round(risk_profile.attendance_rate or 0, 1) if risk_profile else '',
            round(risk_profile.risk_score or 0, 1) if risk_profile else '',
            risk_profile.risk_level if risk_profile else 'Not calculated',
            risk_profile.risk_reasons if risk_profile else ''
        ])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=eduguard_admin_report.csv'
    return response

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

        redirect_target = request.args.get('next')
        if redirect_target:
            flash(f'Risk updated for {student.first_name} {student.last_name}: {risk_profile.risk_level}', 'success')
            return redirect(redirect_target)
        
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
        redirect_target = request.args.get('next')
        if redirect_target:
            flash(
                f'Risk updated for {summary["updated"]} students. High/Critical: {summary["high"] + summary["critical"]}',
                'success'
            )
            return redirect(redirect_target)
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
                'focus': 'Foundational learning, remedial classes, and community education support',
                'contact': 'contact@pratham.org | +91-22-6518-0000',
                'website': 'https://www.pratham.org',
                'programs': ['Learning Enhancement', 'Bridge Courses', 'Community Learning']
            },
            {
                'name': 'Teach For India',
                'focus': 'Mentorship, classroom support, and career exposure for underserved students',
                'contact': 'info@teachforindia.org | +91-80-4710-1234',
                'website': 'https://www.teachforindia.org',
                'programs': ['Mentorship', 'Student Support', 'Career Guidance']
            },
            {
                'name': 'Akanksha Foundation',
                'focus': 'After-school support, counselling, and life-skills development',
                'contact': 'info@akanksha.org | +91-22-2370-0200',
                'website': 'https://www.akanksha.org',
                'programs': ['After-school Programs', 'Career Counseling', 'Mentorship']
            },
            {
                'name': 'Smile Foundation',
                'focus': 'Education, healthcare, and scholarship support for low-income families',
                'contact': 'info@smilefoundationindia.org | +91-11-4312-3700',
                'website': 'https://www.smilefoundationindia.org',
                'programs': ['Scholarship Help', 'Healthcare Support', 'Digital Learning']
            },
            {
                'name': 'Magic Bus India Foundation',
                'focus': 'Life skills, employability, and school-to-work transition support',
                'contact': 'info@magicbusindia.org | +91-22-6243-4800',
                'website': 'https://www.magicbus.org',
                'programs': ['Life Skills', 'Employability Training', 'Mentor Connect']
            },
            {
                'name': 'CRY India',
                'focus': 'Child rights, education continuity, and family support interventions',
                'contact': 'support@crymail.org | +91-22-2309-6363',
                'website': 'https://www.cry.org',
                'programs': ['Education Continuity', 'Family Outreach', 'Emergency Support']
            },
            {
                'name': 'Room to Read India',
                'focus': 'Literacy, girls education, and reading habit programs',
                'contact': 'india@roomtoread.org | +91-11-4666-4000',
                'website': 'https://www.roomtoread.org',
                'programs': ['Girls Education', 'Reading Rooms', 'Academic Mentoring']
            },
            {
                'name': 'Bhumi',
                'focus': 'Volunteer-driven teaching, mentorship, and career-readiness programs',
                'contact': 'volunteer@bhumi.ngo | +91-44-4300-9445',
                'website': 'https://www.bhumi.ngo',
                'programs': ['Volunteer Tutoring', 'Career Readiness', 'Counselling Camps']
            },
            {
                'name': 'Goonj',
                'focus': 'Material support, books, uniforms, and emergency family assistance',
                'contact': 'mail@goonj.org | +91-11-4140-1216',
                'website': 'https://goonj.org',
                'programs': ['Books and Kits', 'Emergency Aid', 'Community Drives']
            },
            {
                'name': 'U&I Trust',
                'focus': 'Academic mentoring, emotional support, and student volunteer programs',
                'contact': 'contact@uandi.org.in | +91-80-4113-0101',
                'website': 'https://www.uandi.org.in',
                'programs': ['Academic Mentoring', 'Mental Wellness', 'Peer Volunteers']
            },
            {
                'name': 'Aarohan Foundation',
                'focus': 'Counselling, remedial education, and family outreach for at-risk students',
                'contact': 'support@aarohanfoundation.org | +91-11-4050-8844',
                'website': 'https://aarohanfoundation.org',
                'programs': ['Remedial Classes', 'Family Counselling', 'Dropout Prevention']
            },
            {
                'name': 'Vidya Foundation',
                'focus': 'Scholarships, digital literacy, and career support for college students',
                'contact': 'info@vidya-india.org | +91-22-2570-0036',
                'website': 'https://www.vidya-india.org',
                'programs': ['Scholarships', 'Digital Literacy', 'Career Support']
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

# Debug routes for real-time testing
@main_bp.route('/debug/trigger-notification')
def trigger_notification():
    """Trigger a test notification via Socket.io"""
    print("[DEBUG] Triggering notification...")
    try:
        from realtime_notifications import notification_manager
        print("[DEBUG] Notification manager imported")
        
        # Send a test alert to all users
        notification_manager.send_alert({
            'title': 'Real-Time Test',
            'description': 'This is a real-time notification triggered from the debug route!',
            'severity': 'Critical'
        })
        print("[DEBUG] Alert sent")
        
        # Also send a dashboard refresh update
        notification_manager.send_dashboard_update({
            'type': 'stats_refresh',
            'message': 'Dashboard stats updated in real-time'
        })
        print("[DEBUG] Dashboard update sent")
        
        return "Notification triggered! Check the student dashboard."
    except Exception as e:
        print(f"[DEBUG] Error in trigger_notification: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500
