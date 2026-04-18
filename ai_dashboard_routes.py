"""
AI Dashboard Routes
Comprehensive analytics, insights, and predictive analytics
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models_enhanced import db, Scholarship, ScholarshipApplication, Student, User, AnalyticsData, ApplicationStatus, ScholarshipStatus
from datetime import datetime, timedelta, date
from sqlalchemy import func, and_, or_
import json
from rbac_system import admin_required, student_required, get_student_for_current_user

ai_dashboard_bp = Blueprint('ai_dashboard', __name__, url_prefix='/ai-dashboard')

# ================================
# AI Dashboard (Admin)
# ================================

@ai_dashboard_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """AI-powered admin dashboard"""
    
    # Get key metrics
    total_scholarships = Scholarship.query.count()
    active_scholarships = Scholarship.query.filter_by(status=ScholarshipStatus.ACTIVE).count()
    total_applications = ScholarshipApplication.query.count()
    pending_applications = ScholarshipApplication.query.filter_by(status=ApplicationStatus.PENDING).count()
    
    # Application trends (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_applications = ScholarshipApplication.query.filter(
        ScholarshipApplication.application_date >= thirty_days_ago
    ).count()
    
    # Success rate
    approved_applications = ScholarshipApplication.query.filter_by(status=ApplicationStatus.APPROVED).count()
    success_rate = (approved_applications / total_applications * 100) if total_applications > 0 else 0
    
    # Top performing scholarships
    top_scholarships = db.session.query(
        Scholarship.title,
        func.count(ScholarshipApplication.id).label('application_count'),
        func.avg(ScholarshipApplication.ai_success_probability).label('avg_success_prob')
    ).join(ScholarshipApplication).group_by(Scholarship.id).order_by(
        func.count(ScholarshipApplication.id).desc()
    ).limit(5).all()
    
    # Department distribution
    dept_distribution = db.session.query(
        Student.department,
        func.count(Student.id).label('student_count')
    ).group_by(Student.department).order_by(func.count(Student.id).desc()).all()
    
    return render_template('ai_dashboard/admin.html',
                         total_scholarships=total_scholarships,
                         active_scholarships=active_scholarships,
                         total_applications=total_applications,
                         pending_applications=pending_applications,
                         recent_applications=recent_applications,
                         success_rate=success_rate,
                         top_scholarships=top_scholarships,
                         dept_distribution=dept_distribution)

@ai_dashboard_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Detailed analytics page"""
    
    # Date range from request
    days = int(request.args.get('days', 30))
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Application trends over time
    application_trends = db.session.query(
        func.date(ScholarshipApplication.application_date).label('date'),
        func.count(ScholarshipApplication.id).label('count')
    ).filter(
        ScholarshipApplication.application_date >= start_date
    ).group_by(func.date(ScholarshipApplication.application_date)).all()
    
    # Status distribution
    status_distribution = db.session.query(
        ScholarshipApplication.status,
        func.count(ScholarshipApplication.id).label('count')
    ).group_by(ScholarshipApplication.status).all()
    
    # GPA distribution of applicants
    gpa_distribution = db.session.query(
        func.round(Student.gpa, 1).label('gpa'),
        func.count(Student.id).label('count')
    ).join(ScholarshipApplication).group_by(
        func.round(Student.gpa, 1)
    ).order_by(func.round(Student.gpa, 1)).all()
    
    # Financial analysis
    financial_analysis = db.session.query(
        func.avg(Student.annual_income).label('avg_income'),
        func.min(Student.annual_income).label('min_income'),
        func.max(Student.annual_income).label('max_income')
    ).join(ScholarshipApplication).first()
    
    return render_template('ai_dashboard/analytics.html',
                         application_trends=application_trends,
                         status_distribution=status_distribution,
                         gpa_distribution=gpa_distribution,
                         financial_analysis=financial_analysis,
                         days=days)

@ai_dashboard_bp.route('/predictions')
@login_required
@admin_required
def predictions():
    """AI predictions and insights"""
    
    # Predict scholarship demand
    scholarship_demand = predict_scholarship_demand()
    
    # Predict application success rates
    success_predictions = predict_success_rates()
    
    # Identify at-risk students
    at_risk_students = identify_at_risk_students()
    
    # Scholarship recommendations
    scholarship_recommendations = generate_scholarship_recommendations()
    
    return render_template('ai_dashboard/predictions.html',
                         scholarship_demand=scholarship_demand,
                         success_predictions=success_predictions,
                         at_risk_students=at_risk_students,
                         scholarship_recommendations=scholarship_recommendations)

# ================================
# AI Dashboard (Student)
# ================================

@ai_dashboard_bp.route('/student')
@login_required
@student_required
def student_dashboard():
    """AI-powered student dashboard"""
    
    student = get_student_for_current_user()
    if not student:
        return redirect(url_for('auth.login'))
    
    # Student's applications
    my_applications = ScholarshipApplication.query.filter_by(student_id=student.id).all()
    
    # Eligible scholarships
    eligible_scholarships = get_eligible_scholarships(student)
    
    # AI recommendations
    scholarship_recommendations = get_personalized_recommendations(student)
    
    # Academic insights
    academic_insights = get_academic_insights(student)
    
    # Application success probability
    avg_success_prob = calculate_average_success_probability(student)
    
    # Career suggestions based on profile
    career_suggestions = get_career_suggestions(student)
    
    return render_template('ai_dashboard/student.html',
                         student=student,
                         my_applications=my_applications,
                         eligible_scholarships=eligible_scholarships,
                         scholarship_recommendations=scholarship_recommendations,
                         academic_insights=academic_insights,
                         avg_success_prob=avg_success_prob,
                         career_suggestions=career_suggestions)

# ================================
# API Endpoints
# ================================

@ai_dashboard_bp.route('/api/metrics')
@login_required
@admin_required
def api_metrics():
    """API endpoint for dashboard metrics"""
    
    # Real-time metrics
    metrics = {
        'total_scholarships': Scholarship.query.count(),
        'active_scholarships': Scholarship.query.filter_by(status=ScholarshipStatus.ACTIVE).count(),
        'total_applications': ScholarshipApplication.query.count(),
        'pending_applications': ScholarshipApplication.query.filter_by(status=ApplicationStatus.PENDING).count(),
        'approved_applications': ScholarshipApplication.query.filter_by(status=ApplicationStatus.APPROVED).count(),
        'rejected_applications': ScholarshipApplication.query.filter_by(status=ApplicationStatus.REJECTED).count(),
        'total_students': Student.query.count(),
        'average_gpa': db.session.query(func.avg(Student.gpa)).scalar() or 0,
        'average_income': db.session.query(func.avg(Student.annual_income)).scalar() or 0
    }
    
    return jsonify(metrics)

@ai_dashboard_bp.route('/api/trends')
@login_required
@admin_required
def api_trends():
    """API endpoint for application trends"""
    
    days = int(request.args.get('days', 30))
    start_date = datetime.utcnow() - timedelta(days=days)
    
    trends = db.session.query(
        func.date(ScholarshipApplication.application_date).label('date'),
        func.count(ScholarshipApplication.id).label('count'),
        func.sum(func.case([(ScholarshipApplication.status == ApplicationStatus.APPROVED, 1)], else_=0)).label('approved'),
        func.sum(func.case([(ScholarshipApplication.status == ApplicationStatus.REJECTED, 1)], else_=0)).label('rejected')
    ).filter(
        ScholarshipApplication.application_date >= start_date
    ).group_by(func.date(ScholarshipApplication.application_date)).all()
    
    data = []
    for trend in trends:
        data.append({
            'date': trend.date.isoformat(),
            'total': trend.count,
            'approved': trend.approved or 0,
            'rejected': trend.rejected or 0
        })
    
    return jsonify(data)

@ai_dashboard_bp.route('/api/recommendations/<int:student_id>')
@login_required
@admin_required
def api_student_recommendations(student_id):
    """API endpoint for student recommendations"""
    
    student = Student.query.get_or_404(student_id)
    recommendations = get_personalized_recommendations(student)
    
    return jsonify(recommendations)

@ai_dashboard_bp.route('/api/student-insights')
@login_required
@student_required
def api_student_insights():
    """API endpoint for student personal insights"""
    
    student = get_student_for_current_user()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    insights = {
        'academic_performance': get_academic_insights(student),
        'scholarship_recommendations': get_personalized_recommendations(student),
        'success_probability': calculate_average_success_probability(student),
        'career_suggestions': get_career_suggestions(student),
        'application_tips': generate_application_tips(student)
    }
    
    return jsonify(insights)

# ================================
# AI Helper Functions
# ================================

def predict_scholarship_demand():
    """Predict scholarship demand for next period"""
    
    # Historical data
    historical_data = db.session.query(
        func.date_trunc('month', ScholarshipApplication.application_date).label('month'),
        func.count(ScholarshipApplication.id).label('applications')
    ).group_by(
        func.date_trunc('month', ScholarshipApplication.application_date)
    ).order_by('month').limit(12).all()
    
    # Simple linear regression for prediction
    if len(historical_data) >= 3:
        months = list(range(len(historical_data)))
        applications = [data.applications for data in historical_data]
        
        # Calculate trend
        n = len(applications)
        sum_x = sum(months)
        sum_y = sum(applications)
        sum_xy = sum(months[i] * applications[i] for i in range(n))
        sum_x2 = sum(x * x for x in months)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Predict next 3 months
        predictions = []
        for i in range(1, 4):
            predicted = slope * (n + i) + intercept
            predictions.append({
                'month': f'Next Month {i}',
                'predicted_applications': max(0, int(predicted))
            })
        
        return predictions
    
    return []

def predict_success_rates():
    """Predict success rates for different scholarship categories"""
    
    scholarships = Scholarship.query.filter_by(status=ScholarshipStatus.ACTIVE).all()
    
    predictions = []
    for scholarship in scholarships:
        applications = ScholarshipApplication.query.filter_by(scholarship_id=scholarship.id).all()
        
        if applications:
            approved = sum(1 for app in applications if app.status == ApplicationStatus.APPROVED)
            historical_success_rate = approved / len(applications)
            
            # AI adjustment based on current trends
            recent_applications = [app for app in applications 
                                if app.application_date >= datetime.utcnow() - timedelta(days=30)]
            
            if recent_applications:
                recent_success_rate = sum(1 for app in recent_applications 
                                        if app.status == ApplicationStatus.APPROVED) / len(recent_applications)
                
                # Weight recent trends more heavily
                predicted_rate = (historical_success_rate * 0.3 + recent_success_rate * 0.7)
            else:
                predicted_rate = historical_success_rate
            
            predictions.append({
                'scholarship': scholarship.title,
                'current_success_rate': historical_success_rate * 100,
                'predicted_success_rate': predicted_rate * 100,
                'confidence': min(95, len(applications) * 5)  # Confidence based on sample size
            })
    
    return predictions

def identify_at_risk_students():
    """Identify students at risk of academic or financial issues"""
    
    # Academic risk factors
    academic_risk_students = Student.query.filter(
        or_(
            Student.gpa < 2.5,
            Student.attendance_rate < 75,
            Student.credits_completed < 30
        )
    ).all()
    
    # Financial risk factors
    financial_risk_students = Student.query.filter(
        or_(
            Student.annual_income < 20000,
            Student.financial_need_level == 'High'
        )
    ).all()
    
    # Combine and score
    at_risk = []
    for student in academic_risk_students + financial_risk_students:
        risk_score = 0
        risk_factors = []
        
        if student.gpa and student.gpa < 2.5:
            risk_score += 30
            risk_factors.append('Low GPA')
        
        if student.attendance_rate and student.attendance_rate < 75:
            risk_score += 25
            risk_factors.append('Poor Attendance')
        
        if student.credits_completed and student.credits_completed < 30:
            risk_score += 20
            risk_factors.append('Insufficient Credits')
        
        if student.annual_income and student.annual_income < 20000:
            risk_score += 25
            risk_factors.append('Low Income')
        
        if student.financial_need_level == 'High':
            risk_score += 15
            risk_factors.append('High Financial Need')
        
        if risk_score > 0:
            at_risk.append({
                'student': student,
                'risk_score': min(risk_score, 100),
                'risk_factors': risk_factors
            })
    
    # Sort by risk score
    at_risk.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return at_risk[:10]  # Top 10 at-risk students

def generate_scholarship_recommendations():
    """Generate recommendations for new scholarships"""
    
    # Analyze current scholarship gaps
    current_scholarships = Scholarship.query.all()
    
    # Common departments
    dept_counts = db.session.query(
        Student.department,
        func.count(Student.id).label('count')
    ).group_by(Student.department).order_by(func.count(Student.id).desc()).all()
    
    # Average GPA by department
    dept_gpas = db.session.query(
        Student.department,
        func.avg(Student.gpa).label('avg_gpa')
    ).group_by(Student.department).all()
    
    recommendations = []
    
    # Recommend scholarships for departments with high demand but low supply
    for dept, count in dept_counts[:5]:
        dept_scholarships = [s for s in current_scholarships 
                           if s.departments and dept in json.loads(s.departments)]
        
        if len(dept_scholarships) < count / 50:  # Less than 1 scholarship per 50 students
            avg_gpa = next((gpa for d, gpa in dept_gpas if d == dept), 3.0)
            
            recommendations.append({
                'type': 'Department-specific',
                'target_department': dept,
                'suggested_amount': 5000 if avg_gpa > 3.5 else 3000,
                'suggested_gpa_requirement': avg_gpa - 0.5,
                'reason': f'High demand ({count} students) with low scholarship supply',
                'priority': 'High' if count > 100 else 'Medium'
            })
    
    # Recommend need-based scholarships
    low_income_students = Student.query.filter(Student.annual_income < 25000).count()
    need_based_scholarships = [s for s in current_scholarships if s.max_income]
    
    if len(need_based_scholarships) < low_income_students / 100:
        recommendations.append({
            'type': 'Need-based',
            'target_income_max': 30000,
            'suggested_amount': 4000,
            'reason': f'High number of low-income students ({low_income_students})',
            'priority': 'High'
        })
    
    return recommendations

def get_eligible_scholarships(student):
    """Get scholarships student is eligible for"""
    
    from scholarship_routes import is_student_eligible
    
    scholarships = Scholarship.query.filter(
        Scholarship.status == ScholarshipStatus.ACTIVE,
        Scholarship.application_deadline > datetime.utcnow()
    ).all()
    
    eligible = []
    for scholarship in scholarships:
        if is_student_eligible(student, scholarship):
            eligible.append(scholarship)
    
    return eligible

def get_personalized_recommendations(student):
    """Get AI-powered scholarship recommendations for student"""
    
    eligible_scholarships = get_eligible_scholarships(student)
    
    # Score and rank scholarships
    recommendations = []
    for scholarship in eligible_scholarships:
        score = 0
        
        # GPA match
        if scholarship.min_gpa and student.gpa:
            gpa_diff = student.gpa - scholarship.min_gpa
            score += min(gpa_diff * 20, 30)
        
        # Financial need match
        if scholarship.max_income and student.annual_income:
            income_ratio = student.annual_income / scholarship.max_income
            score += max(0, (1 - income_ratio) * 25)
        
        # Department match
        if scholarship.departments and student.department:
            departments = json.loads(scholarship.departments)
            if student.department in departments:
                score += 20
        
        # Amount preference (higher amount for students with financial need)
        if student.financial_need_level == 'High':
            score += min(scholarship.amount / 1000, 15)
        
        # AI tags matching
        if scholarship.ai_tags:
            tags = json.loads(scholarship.ai_tags)
            if student.career_interests:
                for tag in tags:
                    if tag.lower() in student.career_interests.lower():
                        score += 10
        
        recommendations.append({
            'scholarship': scholarship,
            'score': score,
            'reason': generate_recommendation_reason(student, scholarship, score)
        })
    
    # Sort by score
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    return recommendations[:5]  # Top 5 recommendations

def generate_recommendation_reason(student, scholarship, score):
    """Generate reason for scholarship recommendation"""
    
    reasons = []
    
    if scholarship.min_gpa and student.gpa and student.gpa >= scholarship.min_gpa + 0.5:
        reasons.append(f"Strong academic match (GPA: {student.gpa})")
    
    if student.financial_need_level == 'High' and scholarship.amount > 5000:
        reasons.append("High financial need with substantial award amount")
    
    if scholarship.departments and student.department:
        departments = json.loads(scholarship.departments)
        if student.department in departments:
            reasons.append(f"Department-specific opportunity for {student.department}")
    
    if scholarship.ai_tags and student.career_interests:
        tags = json.loads(scholarship.ai_tags)
        for tag in tags:
            if tag.lower() in student.career_interests.lower():
                reasons.append(f"Matches your career interests in {tag}")
                break
    
    return "; ".join(reasons) if reasons else "Good match for your profile"

def get_academic_insights(student):
    """Get AI-powered academic insights"""
    
    insights = []
    
    # GPA analysis
    if student.gpa:
        if student.gpa >= 3.5:
            insights.append({
                'type': 'strength',
                'message': f"Excellent academic performance (GPA: {student.gpa})",
                'suggestion': "Focus on scholarships with high GPA requirements for better success rates"
            })
        elif student.gpa >= 3.0:
            insights.append({
                'type': 'moderate',
                'message': f"Good academic performance (GPA: {student.gpa})",
                'suggestion': "Consider scholarships with moderate GPA requirements and strong personal statements"
            })
        else:
            insights.append({
                'type': 'concern',
                'message': f"Academic performance needs improvement (GPA: {student.gpa})",
                'suggestion': "Focus on need-based scholarships and highlight improvement in personal statement"
            })
    
    # Credit progress
    if student.credits_completed:
        if student.credits_completed >= 90:
            insights.append({
                'type': 'strength',
                'message': f"Strong academic progress ({student.credits_completed} credits)",
                'suggestion': "Eligible for upper-level scholarships with credit requirements"
            })
        elif student.credits_completed < 30:
            insights.append({
                'type': 'concern',
                'message': f"Limited academic progress ({student.credits_completed} credits)",
                'suggestion': "Focus on entry-level scholarships and emphasize potential"
            })
    
    # Attendance
    if student.attendance_rate:
        if student.attendance_rate >= 90:
            insights.append({
                'type': 'strength',
                'message': f"Excellent attendance record ({student.attendance_rate}%)",
                'suggestion': "Highlight dedication and consistency in applications"
            })
        elif student.attendance_rate < 75:
            insights.append({
                'type': 'concern',
                'message': f"Poor attendance record ({student.attendance_rate}%)",
                'suggestion': "Improve attendance to strengthen scholarship applications"
            })
    
    return insights

def calculate_average_success_probability(student):
    """Calculate average success probability for student"""
    
    applications = ScholarshipApplication.query.filter_by(student_id=student.id).all()
    
    if applications:
        total_prob = sum(app.ai_success_probability or 0 for app in applications)
        return total_prob / len(applications)
    
    # Calculate based on student profile
    eligible_scholarships = get_eligible_scholarships(student)
    if eligible_scholarships:
        total_prob = 0
        for scholarship in eligible_scholarships:
            from scholarship_routes import calculate_success_probability
            total_prob += calculate_success_probability(student, scholarship)
        return total_prob / len(eligible_scholarships)
    
    return 0.3  # Default 30% probability

def get_career_suggestions(student):
    """Get AI-powered career suggestions"""
    
    suggestions = []
    
    # Based on department
    department_careers = {
        'Computer Science': ['Software Developer', 'Data Scientist', 'AI Engineer', 'Cybersecurity Analyst'],
        'Engineering': ['Mechanical Engineer', 'Civil Engineer', 'Electrical Engineer', 'Project Manager'],
        'Business': ['Business Analyst', 'Marketing Manager', 'Financial Advisor', 'Entrepreneur'],
        'Arts': ['Graphic Designer', 'Content Creator', 'UX Designer', 'Art Director'],
        'Science': ['Research Scientist', 'Lab Technician', 'Medical Professional', 'Environmental Scientist']
    }
    
    if student.department in department_careers:
        careers = department_careers[student.department]
        suggestions.extend([{
            'field': career,
            'reason': f"Matches your {student.department} background",
            'growth_potential': 'High' if 'Engineer' in career or 'Scientist' in career else 'Medium'
        } for career in careers[:3]])
    
    # Based on performance
    if student.gpa and student.gpa >= 3.5:
        suggestions.append({
            'field': 'Research/Academia',
            'reason': 'Strong academic performance suggests research potential',
            'growth_potential': 'High'
        })
    
    # Based on interests
    if student.career_interests:
        interests = student.career_interests.split(',')
        for interest in interests[:2]:
            suggestions.append({
                'field': interest.strip(),
                'reason': 'Based on your stated interests',
                'growth_potential': 'Medium'
            })
    
    return suggestions[:5]  # Top 5 suggestions

def generate_application_tips(student):
    """Generate personalized application tips"""
    
    tips = []
    
    if student.gpa and student.gpa < 3.0:
        tips.append("Focus on personal statements that highlight improvement and potential")
    
    if student.financial_need_level == 'High':
        tips.append("Provide detailed financial justification with supporting documentation")
    
    if not student.credits_completed or student.credits_completed < 30:
        tips.append("Emphasize academic goals and career plans in your applications")
    
    if student.attendance_rate and student.attendance_rate < 80:
        tips.append("Address any attendance issues proactively in your personal statement")
    
    if not tips:
        tips.append("Highlight your unique strengths and experiences in each application")
    
    return tips
