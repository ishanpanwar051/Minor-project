from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Student, RiskProfile, Attendance, AcademicRecord, Intervention
from utils import update_student_risk
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api/v1')

def admin_or faculty_required(f):
    """Decorator to require admin or faculty role for API endpoints"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'faculty']:
            return jsonify({'error': 'Unauthorized access'}), 403
        return f(*args, **kwargs)
    return decorated_function

@api.route('/students', methods=['GET'])
@login_required
@admin_or faculty_required
def get_students():
    """Get all students with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        risk_filter = request.args.get('risk')
        search = request.args.get('search')
        
        query = Student.query.join(RiskProfile)
        
        if risk_filter:
            query = query.filter(RiskProfile.risk_level == risk_filter)
        
        if search:
            query = query.filter(
                (Student.first_name.ilike(f'%{search}%')) |
                (Student.last_name.ilike(f'%{search}%')) |
                (Student.student_id.ilike(f'%{search}%'))
            )
        
        students = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'students': [{
                'id': s.id,
                'student_id': s.student_id,
                'first_name': s.first_name,
                'last_name': s.last_name,
                'email': s.email,
                'semester': s.semester,
                'risk_level': s.risk_profile.risk_level,
                'risk_score': s.risk_profile.risk_score
            } for s in students.items],
            'pagination': {
                'page': students.page,
                'pages': students.pages,
                'per_page': students.per_page,
                'total': students.total
            }
        })
    except Exception as e:
        logger.error(f"Error in get_students API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/students/<int:student_id>', methods=['GET'])
@login_required
def get_student(student_id):
    """Get detailed information about a specific student"""
    try:
        # Security check: students can only view their own profile
        if current_user.role == 'student':
            student_record = Student.query.filter_by(email=current_user.email).first()
            if not student_record or student_record.id != student_id:
                return jsonify({'error': 'Unauthorized access'}), 403
        
        student = Student.query.get_or_404(student_id)
        risk_profile = update_student_risk(student)
        
        # Get recent records
        attendance = Attendance.query.filter_by(student_id=student_id)\
            .order_by(Attendance.date.desc()).limit(30).all()
        
        academics = AcademicRecord.query.filter_by(student_id=student_id)\
            .order_by(AcademicRecord.date.desc()).all()
        
        interventions = Intervention.query.filter_by(student_id=student_id)\
            .order_by(Intervention.date.desc()).all()
        
        return jsonify({
            'student': {
                'id': student.id,
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone': student.phone,
                'semester': student.semester,
                'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None
            },
            'risk_profile': {
                'risk_score': risk_profile.risk_score,
                'risk_level': risk_profile.risk_level,
                'attendance_factor': risk_profile.attendance_factor,
                'academic_factor': risk_profile.academic_factor,
                'last_updated': risk_profile.last_updated.isoformat()
            },
            'attendance': [{
                'date': a.date.isoformat(),
                'status': a.status
            } for a in attendance],
            'academics': [{
                'subject': a.subject,
                'score': a.score,
                'max_score': a.max_score,
                'exam_type': a.exam_type,
                'date': a.date.isoformat(),
                'percentage': round((a.score / a.max_score) * 100, 2) if a.max_score > 0 else 0
            } for a in academics],
            'interventions': [{
                'type': i.type,
                'notes': i.notes,
                'status': i.status,
                'date': i.date.isoformat()
            } for i in interventions]
        })
    except Exception as e:
        logger.error(f"Error in get_student API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/students/<int:student_id>/attendance', methods=['POST'])
@login_required
@admin_or faculty_required
def add_attendance(student_id):
    """Add attendance record for a student"""
    try:
        data = request.get_json()
        
        if not data or 'date' not in data or 'status' not in data:
            return jsonify({'error': 'Missing required fields: date, status'}), 400
        
        attendance = Attendance(
            student_id=student_id,
            date=datetime.fromisoformat(data['date']).date(),
            status=data['status']
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        # Update risk profile
        student = Student.query.get(student_id)
        update_student_risk(student)
        
        return jsonify({
            'message': 'Attendance recorded successfully',
            'attendance': {
                'id': attendance.id,
                'date': attendance.date.isoformat(),
                'status': attendance.status
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error in add_attendance API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/students/<int:student_id>/academics', methods=['POST'])
@login_required
@admin_or faculty_required
def add_academic_record(student_id):
    """Add academic record for a student"""
    try:
        data = request.get_json()
        
        required_fields = ['subject', 'score', 'max_score', 'exam_type', 'date']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
        
        academic = AcademicRecord(
            student_id=student_id,
            subject=data['subject'],
            score=float(data['score']),
            max_score=float(data['max_score']),
            exam_type=data['exam_type'],
            date=datetime.fromisoformat(data['date']).date()
        )
        
        db.session.add(academic)
        db.session.commit()
        
        # Update risk profile
        student = Student.query.get(student_id)
        update_student_risk(student)
        
        return jsonify({
            'message': 'Academic record added successfully',
            'academic': {
                'id': academic.id,
                'subject': academic.subject,
                'score': academic.score,
                'max_score': academic.max_score,
                'exam_type': academic.exam_type,
                'date': academic.date.isoformat(),
                'percentage': round((academic.score / academic.max_score) * 100, 2)
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error in add_academic_record API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/students/<int:student_id>/interventions', methods=['POST'])
@login_required
@admin_or faculty_required
def add_intervention_api(student_id):
    """Add intervention for a student"""
    try:
        data = request.get_json()
        
        if not data or 'type' not in data or 'notes' not in data:
            return jsonify({'error': 'Missing required fields: type, notes'}), 400
        
        intervention = Intervention(
            student_id=student_id,
            type=data['type'],
            notes=data['notes'],
            date=datetime.utcnow().date()
        )
        
        db.session.add(intervention)
        db.session.commit()
        
        # Send notification email
        from email_service import send_intervention_notification
        student = Student.query.get(student_id)
        send_intervention_notification(student, intervention)
        
        return jsonify({
            'message': 'Intervention recorded successfully',
            'intervention': {
                'id': intervention.id,
                'type': intervention.type,
                'notes': intervention.notes,
                'status': intervention.status,
                'date': intervention.date.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error in add_intervention API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/dashboard/stats', methods=['GET'])
@login_required
@admin_or faculty_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_students = Student.query.count()
        high_risk_count = RiskProfile.query.filter_by(risk_level='High').count()
        medium_risk_count = RiskProfile.query.filter_by(risk_level='Medium').count()
        low_risk_count = RiskProfile.query.filter_by(risk_level='Low').count()
        
        # Recent interventions
        recent_interventions = Intervention.query.order_by(Intervention.date.desc())\
            .limit(5).all()
        
        # Risk distribution by semester
        risk_by_semester = db.session.query(
            Student.semester,
            RiskProfile.risk_level,
            db.func.count(RiskProfile.id).label('count')
        ).join(RiskProfile).group_by(Student.semester, RiskProfile.risk_level).all()
        
        return jsonify({
            'overview': {
                'total_students': total_students,
                'high_risk': high_risk_count,
                'medium_risk': medium_risk_count,
                'low_risk': low_risk_count
            },
            'recent_interventions': [{
                'student_name': i.student.full_name(),
                'type': i.type,
                'date': i.date.isoformat(),
                'status': i.status
            } for i in recent_interventions],
            'risk_by_semester': [
                {
                    'semester': item.semester,
                    'risk_level': item.risk_level,
                    'count': item.count
                } for item in risk_by_semester
            ]
        })
    except Exception as e:
        logger.error(f"Error in get_dashboard_stats API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/analytics/risk-trends', methods=['GET'])
@login_required
@admin_or faculty_required
def get_risk_trends():
    """Get risk trends over time"""
    try:
        # Get risk data for the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        risk_trends = db.session.query(
            db.func.date(RiskProfile.last_updated).label('date'),
            RiskProfile.risk_level,
            db.func.count(RiskProfile.id).label('count')
        ).filter(RiskProfile.last_updated >= thirty_days_ago)\
         .group_by(db.func.date(RiskProfile.last_updated), RiskProfile.risk_level)\
         .order_by(db.func.date(RiskProfile.last_updated)).all()
        
        return jsonify({
            'trends': [
                {
                    'date': item.date.isoformat(),
                    'risk_level': item.risk_level,
                    'count': item.count
                } for item in risk_trends
            ]
        })
    except Exception as e:
        logger.error(f"Error in get_risk_trends API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
