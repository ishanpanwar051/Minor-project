from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.auth_service import AuthorizationError
from services.student_service import StudentService
from services.risk_service import DropoutRiskService
from models_new import UserRole
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

def api_admin_required(f):
    """Decorator to require admin role for API endpoints"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Admin access required',
                'status_code': 403
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def api_teacher_or_admin_required(f):
    """Decorator to require teacher or admin role for API endpoints"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_teacher() or current_user.is_admin()):
            return jsonify({
                'success': False,
                'message': 'Teacher or admin access required',
                'status_code': 403
            }), 403
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'EduGuard API is running',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@api_bp.route('/dashboard/stats')
@login_required
@api_teacher_or_admin_required
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        risk_stats = DropoutRiskService.get_risk_statistics()
        return jsonify({
            'success': True,
            'data': risk_stats
        })
    except Exception as e:
        logger.error(f"API dashboard stats error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred retrieving statistics'
        }), 500

@api_bp.route('/students')
@login_required
@api_teacher_or_admin_required
def get_students():
    """Get students list with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        filters = {}
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        if request.args.get('risk_level'):
            filters['risk_level'] = request.args.get('risk_level')
        if request.args.get('semester'):
            filters['semester'] = int(request.args.get('semester'))
        
        students, total_count = StudentService.get_students(
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'success': True,
            'data': {
                'students': [student.to_dict() for student in students],
                'total_count': total_count,
                'current_page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        logger.error(f"API students error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred retrieving students'
        }), 500

@api_bp.route('/student/<int:student_id>')
@login_required
def get_student(student_id):
    """Get student details"""
    try:
        # Check permissions
        if current_user.is_student():
            from models_new import Student
            student = Student.query.filter_by(user_id=current_user.id).first()
            if not student or student.id != student_id:
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403
        else:
            student = StudentService.get_student_by_id(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'message': 'Student not found'
            }), 404
        
        # Get additional data
        risk_profile = DropoutRiskService.calculate_student_risk(student.id)
        attendance = StudentService.get_student_attendance(student.id, days=30)
        academics = StudentService.get_student_academics(student.id)
        interventions = StudentService.get_student_interventions(student.id)
        
        return jsonify({
            'success': True,
            'data': {
                'student': student.to_dict(),
                'risk_profile': risk_profile.to_dict(),
                'attendance': [att.to_dict() for att in attendance],
                'academics': [acad.to_dict() for acad in academics],
                'interventions': [interv.to_dict() for interv in interventions]
            }
        })
    except Exception as e:
        logger.error(f"API student detail error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred retrieving student details'
        }), 500

@api_bp.route('/student', methods=['POST'])
@login_required
@api_teacher_or_admin_required
def create_student():
    """Create new student"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        success, student, message = StudentService.create_student(
            student_data=data,
            creator_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': student.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"API create student error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred creating student'
        }), 500

@api_bp.route('/student/<int:student_id>', methods=['PUT'])
@login_required
@api_teacher_or_admin_required
def update_student(student_id):
    """Update student"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        success, student, message = StudentService.update_student(
            student_id=student_id,
            student_data=data,
            updater_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': student.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"API update student error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred updating student'
        }), 500

@api_bp.route('/student/<int:student_id>/attendance', methods=['POST'])
@login_required
@api_teacher_or_admin_required
def add_attendance(student_id):
    """Add attendance record"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        success, attendance, message = StudentService.add_attendance_record(
            student_id=student_id,
            attendance_data=data,
            creator_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': attendance.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"API add attendance error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred adding attendance record'
        }), 500

@api_bp.route('/student/<int:student_id>/academic', methods=['POST'])
@login_required
@api_teacher_or_admin_required
def add_academic(student_id):
    """Add academic record"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        success, academic, message = StudentService.add_academic_record(
            student_id=student_id,
            academic_data=data,
            creator_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': academic.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"API add academic error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred adding academic record'
        }), 500

@api_bp.route('/student/<int:student_id>/intervention', methods=['POST'])
@login_required
@api_teacher_or_admin_required
def add_intervention(student_id):
    """Add intervention"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        success, intervention, message = StudentService.add_intervention(
            student_id=student_id,
            intervention_data=data,
            creator_id=current_user.id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': intervention.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"API add intervention error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred adding intervention'
        }), 500

@api_bp.route('/risk/update', methods=['POST'])
@login_required
@api_teacher_or_admin_required
def update_risk_scores():
    """Update risk scores for students"""
    try:
        data = request.get_json()
        student_ids = data.get('student_ids') if data else None
        
        result = DropoutRiskService.batch_update_risk_scores(student_ids)
        
        return jsonify({
            'success': True,
            'message': 'Risk scores updated successfully',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"API update risk scores error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred updating risk scores'
        }), 500

@api_bp.route('/analytics/risk-trends')
@login_required
@api_teacher_or_admin_required
def risk_trends():
    """Get risk trend analytics"""
    try:
        # Get risk statistics
        stats = DropoutRiskService.get_risk_statistics()
        
        # Get students by risk level
        high_risk_students, _ = StudentService.get_students(
            filters={'risk_level': 'High'},
            per_page=100
        )
        medium_risk_students, _ = StudentService.get_students(
            filters={'risk_level': 'Medium'},
            per_page=100
        )
        low_risk_students, _ = StudentService.get_students(
            filters={'risk_level': 'Low'},
            per_page=100
        )
        
        return jsonify({
            'success': True,
            'data': {
                'statistics': stats,
                'risk_distribution': {
                    'high': len(high_risk_students),
                    'medium': len(medium_risk_students),
                    'low': len(low_risk_students)
                },
                'high_risk_students': [student.to_dict() for student in high_risk_students[:10]],
                'medium_risk_students': [student.to_dict() for student in medium_risk_students[:10]],
                'low_risk_students': [student.to_dict() for student in low_risk_students[:10]]
            }
        })
        
    except Exception as e:
        logger.error(f"API risk trends error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred retrieving risk trends'
        }), 500

@api_bp.route('/profile')
@login_required
def get_profile():
    """Get current user profile"""
    try:
        return jsonify({
            'success': True,
            'data': current_user.to_dict()
        })
    except Exception as e:
        logger.error(f"API profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred retrieving profile'
        }), 500
