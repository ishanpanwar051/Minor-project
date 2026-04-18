"""
Scholarship Management Routes
Complete CRUD operations and application management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models_enhanced import db, Scholarship, ScholarshipApplication, Student, User, ApplicationStatus, ScholarshipStatus
from datetime import datetime, timedelta
import json
from rbac_system import admin_required, student_required, get_student_for_current_user

scholarship_bp = Blueprint('scholarship', __name__, url_prefix='/scholarship')

# ================================
# Scholarship Management (Admin)
# ================================

@scholarship_bp.route('/manage')
@login_required
@admin_required
def manage_scholarships():
    """Admin scholarship management dashboard"""
    scholarships = Scholarship.query.order_by(Scholarship.created_at.desc()).all()
    return render_template('scholarship/manage.html', scholarships=scholarships)

@scholarship_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_scholarship():
    """Create new scholarship"""
    if request.method == 'POST':
        try:
            scholarship = Scholarship(
                title=request.form.get('title'),
                description=request.form.get('description'),
                provider=request.form.get('provider'),
                amount=float(request.form.get('amount')),
                currency=request.form.get('currency', 'USD'),
                payment_frequency=request.form.get('payment_frequency'),
                min_gpa=float(request.form.get('min_gpa')) if request.form.get('min_gpa') else None,
                max_income=float(request.form.get('max_income')) if request.form.get('max_income') else None,
                required_credits=int(request.form.get('required_credits')) if request.form.get('required_credits') else None,
                departments=json.dumps(request.form.getlist('departments')),
                year_level=request.form.get('year_level'),
                nationality_requirements=request.form.get('nationality_requirements'),
                gender_requirements=request.form.get('gender_requirements'),
                application_deadline=datetime.strptime(request.form.get('application_deadline'), '%Y-%m-%d'),
                start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d') if request.form.get('start_date') else None,
                end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d') if request.form.get('end_date') else None,
                required_documents=json.dumps(request.form.getlist('required_documents')),
                application_process=request.form.get('application_process'),
                status=ScholarshipStatus.ACTIVE,
                created_by=current_user.id
            )
            
            db.session.add(scholarship)
            db.session.commit()
            
            flash('Scholarship created successfully!', 'success')
            return redirect(url_for('scholarship.manage_scholarships'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating scholarship: {str(e)}', 'danger')
    
    return render_template('scholarship/create.html')

@scholarship_bp.route('/edit/<int:scholarship_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_scholarship(scholarship_id):
    """Edit existing scholarship"""
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    
    if request.method == 'POST':
        try:
            scholarship.title = request.form.get('title')
            scholarship.description = request.form.get('description')
            scholarship.provider = request.form.get('provider')
            scholarship.amount = float(request.form.get('amount'))
            scholarship.currency = request.form.get('currency', 'USD')
            scholarship.payment_frequency = request.form.get('payment_frequency')
            scholarship.min_gpa = float(request.form.get('min_gpa')) if request.form.get('min_gpa') else None
            scholarship.max_income = float(request.form.get('max_income')) if request.form.get('max_income') else None
            scholarship.required_credits = int(request.form.get('required_credits')) if request.form.get('required_credits') else None
            scholarship.departments = json.dumps(request.form.getlist('departments'))
            scholarship.year_level = request.form.get('year_level')
            scholarship.nationality_requirements = request.form.get('nationality_requirements')
            scholarship.gender_requirements = request.form.get('gender_requirements')
            scholarship.application_deadline = datetime.strptime(request.form.get('application_deadline'), '%Y-%m-%d')
            scholarship.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d') if request.form.get('start_date') else None
            scholarship.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d') if request.form.get('end_date') else None
            scholarship.required_documents = json.dumps(request.form.getlist('required_documents'))
            scholarship.application_process = request.form.get('application_process')
            scholarship.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Scholarship updated successfully!', 'success')
            return redirect(url_for('scholarship.manage_scholarships'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating scholarship: {str(e)}', 'danger')
    
    return render_template('scholarship/edit.html', scholarship=scholarship)

@scholarship_bp.route('/delete/<int:scholarship_id>', methods=['POST'])
@login_required
@admin_required
def delete_scholarship(scholarship_id):
    """Delete scholarship"""
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    
    try:
        db.session.delete(scholarship)
        db.session.commit()
        flash('Scholarship deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting scholarship: {str(e)}', 'danger')
    
    return redirect(url_for('scholarship.manage_scholarships'))

# ================================
# Scholarship Applications (Admin)
# ================================

@scholarship_bp.route('/applications')
@login_required
@admin_required
def view_applications():
    """View all scholarship applications"""
    status_filter = request.args.get('status', 'all')
    
    query = ScholarshipApplication.query.join(Scholarship).join(Student).join(User)
    
    if status_filter != 'all':
        query = query.filter(ScholarshipApplication.status == ApplicationStatus[status_filter.upper()])
    
    applications = query.order_by(ScholarshipApplication.application_date.desc()).all()
    
    return render_template('scholarship/applications.html', 
                         applications=applications, 
                         status_filter=status_filter)

@scholarship_bp.route('/application/<int:application_id>/review', methods=['GET', 'POST'])
@login_required
@admin_required
def review_application(application_id):
    """Review scholarship application"""
    application = ScholarshipApplication.query.get_or_404(application_id)
    
    if request.method == 'POST':
        try:
            application.status = ApplicationStatus[request.form.get('status').upper()]
            application.reviewed_by = current_user.id
            application.review_date = datetime.utcnow()
            application.review_comments = request.form.get('review_comments')
            
            db.session.commit()
            
            # Send notification to student
            from models_enhanced import Notification
            notification = Notification(
                user_id=application.student.user_id,
                title=f'Application Status Update: {application.scholarship.title}',
                message=f'Your application status has been updated to: {application.status.value}',
                notification_type='scholarship',
                action_url=url_for('scholarship.my_applications')
            )
            db.session.add(notification)
            db.session.commit()
            
            flash('Application reviewed successfully!', 'success')
            return redirect(url_for('scholarship.view_applications'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error reviewing application: {str(e)}', 'danger')
    
    return render_template('scholarship/review.html', application=application)

# ================================
# Scholarship Portal (Student)
# ================================

@scholarship_bp.route('/')
@login_required
def scholarship_portal():
    """Student scholarship portal"""
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get available scholarships
    scholarships = Scholarship.query.filter(
        Scholarship.status == ScholarshipStatus.ACTIVE,
        Scholarship.application_deadline > datetime.utcnow()
    ).all()
    
    # Filter by eligibility
    eligible_scholarships = []
    for scholarship in scholarships:
        if is_student_eligible(student, scholarship):
            eligible_scholarships.append(scholarship)
    
    # Get student's applications
    my_applications = ScholarshipApplication.query.filter_by(student_id=student.id).all()
    
    return render_template('scholarship/portal.html', 
                         scholarships=eligible_scholarships,
                         my_applications=my_applications,
                         student=student)

@scholarship_bp.route('/apply/<int:scholarship_id>', methods=['GET', 'POST'])
@login_required
@student_required
def apply_scholarship(scholarship_id):
    """Apply for scholarship"""
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found', 'danger')
        return redirect(url_for('auth.login'))
    
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    
    # Check if already applied
    existing_application = ScholarshipApplication.query.filter_by(
        scholarship_id=scholarship_id,
        student_id=student.id
    ).first()
    
    if existing_application:
        flash('You have already applied for this scholarship', 'warning')
        return redirect(url_for('scholarship.scholarship_portal'))
    
    # Check eligibility
    if not is_student_eligible(student, scholarship):
        flash('You are not eligible for this scholarship', 'danger')
        return redirect(url_for('scholarship.scholarship_portal'))
    
    if request.method == 'POST':
        try:
            application = ScholarshipApplication(
                scholarship_id=scholarship_id,
                student_id=student.id,
                personal_statement=request.form.get('personal_statement'),
                financial_justification=request.form.get('financial_justification'),
                additional_documents=json.dumps(request.form.getlist('documents'))
            )
            
            # Calculate AI eligibility score
            application.ai_eligibility_score = calculate_eligibility_score(student, scholarship)
            application.ai_success_probability = calculate_success_probability(student, scholarship)
            application.ai_recommendations = generate_ai_recommendations(student, scholarship)
            
            db.session.add(application)
            db.session.commit()
            
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('scholarship.scholarship_portal'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting application: {str(e)}', 'danger')
    
    return render_template('scholarship/apply.html', scholarship=scholarship, student=student)

@scholarship_bp.route('/my-applications')
@login_required
@student_required
def my_applications():
    """View student's scholarship applications"""
    student = get_student_for_current_user()
    if not student:
        flash('Student profile not found', 'danger')
        return redirect(url_for('auth.login'))
    
    applications = ScholarshipApplication.query.filter_by(student_id=student.id).order_by(
        ScholarshipApplication.application_date.desc()
    ).all()
    
    return render_template('scholarship/my_applications.html', applications=applications)

# ================================
# API Endpoints
# ================================

@scholarship_bp.route('/api/scholarships')
@login_required
def api_scholarships():
    """API endpoint for scholarships"""
    try:
        print(f"[API] Fetching scholarships for user: {current_user.email}")
        
        scholarships = Scholarship.query.filter_by(status='active').all()
        print(f"[API] Found {len(scholarships)} scholarships")
        
        data = []
        for scholarship in scholarships:
            scholarship_data = {
                'id': scholarship.id,
                'title': scholarship.title,
                'provider': scholarship.provider or 'Unknown',
                'amount': scholarship.amount,
                'currency': scholarship.currency or 'USD',
                'deadline': scholarship.application_deadline.isoformat() if scholarship.application_deadline else None,
                'description': scholarship.description[:200] + '...' if scholarship.description and len(scholarship.description) > 200 else (scholarship.description or 'No description available'),
                'min_gpa': scholarship.min_gpa,
                'status': scholarship.status
            }
            data.append(scholarship_data)
        
        print(f"[API] Returning {len(data)} scholarships")
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        print(f"[API ERROR] Failed to fetch scholarships: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@scholarship_bp.route('/api/my-applications')
@login_required
@student_required
def api_my_applications():
    """API endpoint for student's applications"""
    try:
        print(f"[API] Fetching applications for user: {current_user.email}")
        
        student = get_student_for_current_user()
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student profile not found',
                'data': []
            }), 404
        
        applications = ScholarshipApplication.query.filter_by(student_id=student.id).all()
        print(f"[API] Found {len(applications)} applications")
        
        data = []
        for app in applications:
            scholarship = Scholarship.query.get(app.scholarship_id)
            app_data = {
                'id': app.id,
                'scholarship_id': app.scholarship_id,
                'scholarship_title': scholarship.title if scholarship else 'Unknown',
                'status': app.status,
                'application_date': app.application_date.isoformat() if app.application_date else None,
                'gpa_at_application': app.gpa_at_application,
                'ai_eligibility_score': app.ai_eligibility_score,
                'ai_success_probability': app.ai_success_probability
            }
            data.append(app_data)
        
        print(f"[API] Returning {len(data)} applications")
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        print(f"[API ERROR] Failed to fetch applications: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@scholarship_bp.route('/api/eligibility/<int:scholarship_id>')
@login_required
@student_required
def api_check_eligibility(scholarship_id):
    """API endpoint to check eligibility"""
    try:
        print(f"[API] Checking eligibility for scholarship {scholarship_id}")
        
        student = get_student_for_current_user()
        if not student:
            return jsonify({
                'success': False,
                'error': 'Student profile not found',
                'eligible': False
            }), 404
        
        scholarship = Scholarship.query.get_or_404(scholarship_id)
        
        # Simple eligibility check
        eligible = True
        reasons = []
        
        if scholarship.min_gpa and student.gpa < scholarship.min_gpa:
            eligible = False
            reasons.append(f"GPA too low (required: {scholarship.min_gpa}, yours: {student.gpa})")
        
        print(f"[API] Eligibility result: {eligible}")
        return jsonify({
            'success': True,
            'eligible': eligible,
            'reasons': reasons,
            'student_gpa': student.gpa,
            'required_gpa': scholarship.min_gpa
        })
        
    except Exception as e:
        print(f"[API ERROR] Failed to check eligibility: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'eligible': False
        }), 500

# ================================
# Helper Functions
# ================================

def is_student_eligible(student, scholarship):
    """Check if student is eligible for scholarship"""
    # GPA requirement
    if scholarship.min_gpa and (student.gpa or 0) < scholarship.min_gpa:
        return False
    
    # Income requirement
    if scholarship.max_income and (student.annual_income or float('inf')) > scholarship.max_income:
        return False
    
    # Credits requirement
    if scholarship.required_credits and (student.credits_completed or 0) < scholarship.required_credits:
        return False
    
    # Department requirement
    if scholarship.departments:
        eligible_departments = json.loads(scholarship.departments)
        if eligible_departments and student.department not in eligible_departments:
            return False
    
    # Year level requirement
    if scholarship.year_level:
        year_mapping = {'1': 'Freshman', '2': 'Sophomore', '3': 'Junior', '4': 'Senior'}
        student_year = year_mapping.get(str(student.year), '')
        if scholarship.year_level != student_year:
            return False
    
    return True

def calculate_eligibility_score(student, scholarship):
    """Calculate AI eligibility score (0-100)"""
    score = 50  # Base score
    
    # GPA scoring
    if scholarship.min_gpa and student.gpa:
        gpa_diff = student.gpa - scholarship.min_gpa
        score += min(gpa_diff * 20, 30)  # Max 30 points for GPA
    
    # Financial need scoring
    if scholarship.max_income and student.annual_income:
        income_ratio = student.annual_income / scholarship.max_income
        score += max(0, (1 - income_ratio) * 20)  # Max 20 points for financial need
    
    # Academic progress scoring
    if student.credits_completed and scholarship.required_credits:
        credit_ratio = student.credits_completed / scholarship.required_credits
        score += min(credit_ratio * 10, 10)  # Max 10 points for academic progress
    
    return min(score, 100)

def calculate_success_probability(student, scholarship):
    """Calculate AI success probability"""
    base_prob = 0.3  # Base 30% success rate
    
    # Increase based on eligibility score
    eligibility_score = calculate_eligibility_score(student, scholarship)
    base_prob += (eligibility_score / 100) * 0.4  # Max 40% from eligibility
    
    # Adjust based on competition (number of applications vs available slots)
    application_count = ScholarshipApplication.query.filter_by(scholarship_id=scholarship.id).count()
    if application_count > 0:
        competition_factor = min(0.3, 10 / application_count)  # Less competition = higher chance
        base_prob += competition_factor
    
    return min(base_prob, 0.95)  # Max 95% success probability

def generate_ai_recommendations(student, scholarship):
    """Generate AI recommendations for application improvement"""
    recommendations = []
    
    if student.gpa and scholarship.min_gpa and student.gpa < scholarship.min_gpa + 0.5:
        recommendations.append("Consider highlighting academic improvements in your personal statement")
    
    if student.annual_income and scholarship.max_income:
        if student.annual_income > scholarship.max_income * 0.8:
            recommendations.append("Provide detailed financial justification in your application")
    
    if not student.credits_completed or student.credits_completed < 30:
        recommendations.append("Emphasize your academic potential and future plans")
    
    return "; ".join(recommendations) if recommendations else "Strong candidate profile"

def get_eligibility_details(student, scholarship):
    """Get detailed eligibility information"""
    details = {
        'gpa_met': True,
        'income_met': True,
        'credits_met': True,
        'department_met': True,
        'year_met': True
    }
    
    if scholarship.min_gpa and (student.gpa or 0) < scholarship.min_gpa:
        details['gpa_met'] = False
    
    if scholarship.max_income and (student.annual_income or float('inf')) > scholarship.max_income:
        details['income_met'] = False
    
    if scholarship.required_credits and (student.credits_completed or 0) < scholarship.required_credits:
        details['credits_met'] = False
    
    if scholarship.departments:
        eligible_departments = json.loads(scholarship.departments)
        if eligible_departments and student.department not in eligible_departments:
            details['department_met'] = False
    
    if scholarship.year_level:
        year_mapping = {'1': 'Freshman', '2': 'Sophomore', '3': 'Junior', '4': 'Senior'}
        student_year = year_mapping.get(str(student.year), '')
        if scholarship.year_level != student_year:
            details['year_met'] = False
    
    return details
