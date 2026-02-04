"""
Enhanced Backend API for Early Warning System (EWS)
RESTful API with ML Integration, Analytics, and Background Jobs
"""

from flask import Flask, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import json
import logging
from functools import wraps
from models_ews import *

logger = logging.getLogger(__name__)

# API Decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def teacher_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin() or current_user.is_teacher()):
            return jsonify({'error': 'Teacher or admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

class EarlyWarningAPI:
    """Enhanced API for Early Warning System"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize API with Flask app"""
        self.app = app
        self.register_routes()
        self.load_ml_model()
    
    def load_ml_model(self):
        """Load ML model for risk prediction"""
        try:
            self.ml_model = joblib.load('model/model.pkl')
            self.scaler = joblib.load('model/scaler.pkl')
            self.features = joblib.load('model/features.pkl')
            logger.info("ML model loaded successfully")
        except FileNotFoundError:
            logger.warning("ML model not found, using rule-based prediction")
            self.ml_model = None
            self.scaler = None
            self.features = None
    
    def register_routes(self):
        """Register all API routes"""
        
        # Student Management APIs
        @self.app.route('/api/students', methods=['GET'])
        @teacher_or_admin_required
        def get_students():
            """Get all students with filtering and pagination"""
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 20, type=int)
                search = request.args.get('search', '')
                grade = request.args.get('grade', '')
                risk_level = request.args.get('risk_level', '')
                
                query = Student.query
                
                # Apply filters
                if search:
                    query = query.filter(
                        (Student.first_name.ilike(f'%{search}%')) |
                        (Student.last_name.ilike(f'%{search}%')) |
                        (Student.student_id.ilike(f'%{search}%'))
                    )
                
                if grade:
                    query = query.filter(Student.grade == grade)
                
                if risk_level:
                    query = query.join(RiskProfile).filter(RiskProfile.risk_level == risk_level)
                
                # Pagination
                students = query.paginate(page=page, per_page=per_page, error_out=False)
                
                return jsonify({
                    'students': [self.serialize_student(student) for student in students.items],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': students.total,
                        'pages': students.pages,
                        'has_next': students.has_next,
                        'has_prev': students.has_prev
                    }
                })
            except Exception as e:
                logger.error(f"Error fetching students: {str(e)}")
                return jsonify({'error': 'Failed to fetch students'}), 500
        
        @self.app.route('/api/students/<int:student_id>', methods=['GET'])
        @teacher_or_admin_required
        def get_student(student_id):
            """Get detailed student information"""
            try:
                student = Student.query.get_or_404(student_id)
                
                # Get comprehensive student data
                student_data = self.serialize_student(student)
                student_data['risk_profile'] = self.serialize_risk_profile(student.current_risk_profile())
                student_data['recent_attendance'] = self.serialize_attendance(
                    student.attendance_records.order_by(Attendance.date.desc()).limit(30).all()
                )
                student_data['recent_academics'] = self.serialize_academics(
                    student.academic_records.order_by(AcademicRecord.date.desc()).limit(10).all()
                )
                student_data['active_alerts'] = self.serialize_alerts(student.active_alerts())
                student_data['recent_interventions'] = self.serialize_interventions(
                    student.interventions.order_by(Intervention.created_at.desc()).limit(5).all()
                )
                
                return jsonify(student_data)
            except Exception as e:
                logger.error(f"Error fetching student {student_id}: {str(e)}")
                return jsonify({'error': 'Failed to fetch student'}), 500
        
        @self.app.route('/api/students/<int:student_id>/risk', methods=['GET'])
        @teacher_or_admin_required
        def get_student_risk(student_id):
            """Get student risk analysis with ML prediction"""
            try:
                student = Student.query.get_or_404(student_id)
                
                # Get current risk profile
                risk_profile = student.current_risk_profile()
                
                # Calculate ML prediction if model is available
                ml_prediction = None
                if self.ml_model and risk_profile:
                    ml_prediction = self.predict_ml_risk(risk_profile)
                
                # Get historical risk trends
                risk_history = student.risk_profiles.order_by(RiskProfile.created_at.desc()).limit(30).all()
                
                # Calculate risk factors
                risk_factors = self.calculate_risk_factors(student)
                
                return jsonify({
                    'current_risk': self.serialize_risk_profile(risk_profile),
                    'ml_prediction': ml_prediction,
                    'risk_history': [self.serialize_risk_profile(rp) for rp in risk_history],
                    'risk_factors': risk_factors,
                    'recommendations': self.generate_risk_recommendations(risk_profile, ml_prediction)
                })
            except Exception as e:
                logger.error(f"Error calculating risk for student {student_id}: {str(e)}")
                return jsonify({'error': 'Failed to calculate risk'}), 500
        
        # Alert Management APIs
        @self.app.route('/api/alerts', methods=['GET'])
        @teacher_or_admin_required
        def get_alerts():
            """Get alerts with filtering"""
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 20, type=int)
                status = request.args.get('status', '')
                alert_type = request.args.get('type', '')
                priority = request.args.get('priority', '')
                
                query = Alert.query
                
                # Apply filters
                if status:
                    query = query.filter(Alert.status == status)
                if alert_type:
                    query = query.filter(Alert.type == alert_type)
                if priority:
                    query = query.filter(Alert.priority == priority)
                
                # Order by creation date
                query = query.order_by(Alert.created_at.desc())
                
                # Pagination
                alerts = query.paginate(page=page, per_page=per_page, error_out=False)
                
                return jsonify({
                    'alerts': [self.serialize_alert(alert) for alert in alerts.items],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': alerts.total,
                        'pages': alerts.pages,
                        'has_next': alerts.has_next,
                        'has_prev': alerts.has_prev
                    }
                })
            except Exception as e:
                logger.error(f"Error fetching alerts: {str(e)}")
                return jsonify({'error': 'Failed to fetch alerts'}), 500
        
        @self.app.route('/api/alerts', methods=['POST'])
        @teacher_or_admin_required
        def create_alert():
            """Create new alert"""
            try:
                data = request.get_json()
                
                alert = Alert(
                    student_id=data['student_id'],
                    type=AlertType(data['type']),
                    title=data['title'],
                    message=data['message'],
                    priority=data.get('priority', 'Medium'),
                    risk_score=data.get('risk_score'),
                    created_by=current_user.id
                )
                
                db.session.add(alert)
                db.session.commit()
                
                # Trigger background job for notifications
                self.trigger_alert_notifications(alert)
                
                return jsonify(self.serialize_alert(alert)), 201
            except Exception as e:
                logger.error(f"Error creating alert: {str(e)}")
                db.session.rollback()
                return jsonify({'error': 'Failed to create alert'}), 500
        
        @self.app.route('/api/alerts/<int:alert_id>/resolve', methods=['PUT'])
        @teacher_or_admin_required
        def resolve_alert(alert_id):
            """Resolve an alert"""
            try:
                alert = Alert.query.get_or_404(alert_id)
                data = request.get_json()
                
                alert.status = AlertStatus.RESOLVED
                alert.resolved_by = current_user.id
                alert.resolved_at = datetime.utcnow()
                alert.resolution_notes = data.get('resolution_notes', '')
                
                db.session.commit()
                
                return jsonify(self.serialize_alert(alert))
            except Exception as e:
                logger.error(f"Error resolving alert {alert_id}: {str(e)}")
                return jsonify({'error': 'Failed to resolve alert'}), 500
        
        # Intervention Management APIs
        @self.app.route('/api/interventions', methods=['GET'])
        @teacher_or_admin_required
        def get_interventions():
            """Get interventions with filtering"""
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 20, type=int)
                status = request.args.get('status', '')
                student_id = request.args.get('student_id', type=int)
                
                query = Intervention.query
                
                # Apply filters
                if status:
                    query = query.filter(Intervention.status == status)
                if student_id:
                    query = query.filter(Intervention.student_id == student_id)
                
                # Order by scheduled date
                query = query.order_by(Intervention.scheduled_date.desc())
                
                # Pagination
                interventions = query.paginate(page=page, per_page=per_page, error_out=False)
                
                return jsonify({
                    'interventions': [self.serialize_intervention(intervention) for intervention in interventions.items],
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': interventions.total,
                        'pages': interventions.pages,
                        'has_next': interventions.has_next,
                        'has_prev': interventions.has_prev
                    }
                })
            except Exception as e:
                logger.error(f"Error fetching interventions: {str(e)}")
                return jsonify({'error': 'Failed to fetch interventions'}), 500
        
        @self.app.route('/api/interventions', methods=['POST'])
        @teacher_or_admin_required
        def create_intervention():
            """Create new intervention"""
            try:
                data = request.get_json()
                
                intervention = Intervention(
                    student_id=data['student_id'],
                    type=data['type'],
                    title=data['title'],
                    description=data['description'],
                    priority=data.get('priority', 'Medium'),
                    scheduled_date=datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date(),
                    assigned_to_id=data['assigned_to_id'],
                    created_by=current_user.id
                )
                
                db.session.add(intervention)
                db.session.commit()
                
                return jsonify(self.serialize_intervention(intervention)), 201
            except Exception as e:
                logger.error(f"Error creating intervention: {str(e)}")
                db.session.rollback()
                return jsonify({'error': 'Failed to create intervention'}), 500
        
        # Analytics and Reporting APIs
        @self.app.route('/api/analytics/dashboard', methods=['GET'])
        @admin_required
        def get_dashboard_analytics():
            """Get dashboard analytics"""
            try:
                # Get key metrics
                total_students = Student.query.count()
                active_alerts = Alert.query.filter_by(status=AlertStatus.ACTIVE).count()
                high_risk_students = RiskProfile.query.filter(RiskProfile.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])).count()
                
                # Get risk distribution
                risk_distribution = db.session.query(
                    RiskProfile.risk_level,
                    db.func.count(RiskProfile.id).label('count')
                ).group_by(RiskProfile.risk_level).all()
                
                # Get attendance trends (last 30 days)
                thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
                attendance_trend = db.session.query(
                    Attendance.date,
                    db.func.count(Attendance.id).label('total'),
                    db.func.sum(db.case([(Attendance.status == 'Present', 1)], else_=0)).label('present')
                ).filter(Attendance.date >= thirty_days_ago).group_by(Attendance.date).all()
                
                # Get alert trends
                alert_trend = db.session.query(
                    db.func.date(Alert.created_at).label('date'),
                    db.func.count(Alert.id).label('count')
                ).filter(Alert.created_at >= thirty_days_ago).group_by(db.func.date(Alert.created_at)).all()
                
                return jsonify({
                    'summary': {
                        'total_students': total_students,
                        'active_alerts': active_alerts,
                        'high_risk_students': high_risk_students,
                        'risk_distribution': [{'level': level.value, 'count': count} for level, count in risk_distribution]
                    },
                    'attendance_trend': [
                        {'date': str(date), 'total': total, 'present': present}
                        for date, total, present in attendance_trend
                    ],
                    'alert_trend': [
                        {'date': str(date), 'count': count}
                        for date, count in alert_trend
                    ]
                })
            except Exception as e:
                logger.error(f"Error fetching dashboard analytics: {str(e)}")
                return jsonify({'error': 'Failed to fetch analytics'}), 500
        
        @self.app.route('/api/analytics/performance-trends', methods=['GET'])
        @teacher_or_admin_required
        def get_performance_trends():
            """Get performance trends for students"""
            try:
                student_id = request.args.get('student_id', type=int)
                days = request.args.get('days', 30, type=int)
                
                start_date = datetime.utcnow().date() - timedelta(days=days)
                
                query = PerformanceTrend.query.filter(
                    PerformanceTrend.date >= start_date
                )
                
                if student_id:
                    query = query.filter(PerformanceTrend.student_id == student_id)
                
                trends = query.order_by(PerformanceTrend.date).all()
                
                return jsonify({
                    'trends': [self.serialize_performance_trend(trend) for trend in trends]
                })
            except Exception as e:
                logger.error(f"Error fetching performance trends: {str(e)}")
                return jsonify({'error': 'Failed to fetch trends'}), 500
        
        @self.app.route('/api/analytics/export', methods=['POST'])
        @admin_required
        def export_analytics():
            """Export analytics data"""
            try:
                data = request.get_json()
                export_type = data.get('type', 'students')
                format_type = data.get('format', 'csv')
                
                if export_type == 'students':
                    # Export student data with risk profiles
                    students = Student.query.all()
                    export_data = []
                    
                    for student in students:
                        risk_profile = student.current_risk_profile()
                        student_data = self.serialize_student(student)
                        student_data['risk_score'] = risk_profile.current_risk_score if risk_profile else 0
                        student_data['risk_level'] = risk_profile.risk_level.value if risk_profile else 'LOW'
                        export_data.append(student_data)
                    
                    df = pd.DataFrame(export_data)
                    
                    if format_type == 'csv':
                        csv_data = df.to_csv(index=False)
                        return jsonify({
                            'data': csv_data,
                            'filename': f'students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                        })
                
                return jsonify({'error': 'Invalid export type'}), 400
            except Exception as e:
                logger.error(f"Error exporting data: {str(e)}")
                return jsonify({'error': 'Failed to export data'}), 500
        
        # ML Prediction API
        @self.app.route('/api/ml/predict', methods=['POST'])
        @teacher_or_admin_required
        def predict_dropout_risk():
            """Predict dropout risk using ML model"""
            try:
                data = request.get_json()
                student_id = data.get('student_id')
                
                if not student_id:
                    return jsonify({'error': 'Student ID is required'}), 400
                
                student = Student.query.get_or_404(student_id)
                risk_profile = student.current_risk_profile()
                
                if not risk_profile:
                    return jsonify({'error': 'No risk profile found for student'}), 404
                
                # Use ML model for prediction
                if self.ml_model:
                    prediction = self.predict_ml_risk(risk_profile)
                else:
                    # Fallback to rule-based prediction
                    prediction = self.predict_rule_based_risk(risk_profile)
                
                return jsonify({
                    'student_id': student_id,
                    'prediction': prediction,
                    'recommendations': self.generate_risk_recommendations(risk_profile, prediction)
                })
            except Exception as e:
                logger.error(f"Error in ML prediction: {str(e)}")
                return jsonify({'error': 'Failed to predict risk'}), 500
    
    # Helper Methods
    def serialize_student(self, student):
        """Serialize student object"""
        return {
            'id': student.id,
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'full_name': student.full_name(),
            'email': student.email,
            'phone': student.phone,
            'grade': student.grade,
            'section': student.section,
            'roll_number': student.roll_number,
            'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None,
            'parent_guardian_name': student.parent_guardian_name,
            'parent_guardian_phone': student.parent_guardian_phone,
            'created_at': student.created_at.isoformat()
        }
    
    def serialize_risk_profile(self, risk_profile):
        """Serialize risk profile object"""
        if not risk_profile:
            return None
        return {
            'id': risk_profile.id,
            'current_risk_score': risk_profile.current_risk_score,
            'risk_level': risk_profile.risk_level.value if risk_profile.risk_level else 'LOW',
            'attendance_factor': risk_profile.attendance_factor,
            'academic_factor': risk_profile.academic_factor,
            'behavior_factor': risk_profile.behavior_factor,
            'engagement_factor': risk_profile.engagement_factor,
            'attendance_rate': risk_profile.attendance_rate,
            'average_score': risk_profile.average_score,
            'behavior_score': risk_profile.behavior_score,
            'engagement_score': risk_profile.engagement_score,
            'ml_risk_probability': risk_profile.ml_risk_probability,
            'ml_confidence': risk_profile.ml_confidence,
            'risk_trend': risk_profile.risk_trend,
            'last_updated': risk_profile.last_updated.isoformat()
        }
    
    def serialize_alert(self, alert):
        """Serialize alert object"""
        return {
            'id': alert.id,
            'student_id': alert.student_id,
            'type': alert.type.value,
            'title': alert.title,
            'message': alert.message,
            'status': alert.status.value,
            'priority': alert.priority,
            'risk_score': alert.risk_score,
            'created_at': alert.created_at.isoformat(),
            'escalated': alert.escalated,
            'escalation_level': alert.escalation_level
        }
    
    def serialize_intervention(self, intervention):
        """Serialize intervention object"""
        return {
            'id': intervention.id,
            'student_id': intervention.student_id,
            'type': intervention.type,
            'title': intervention.title,
            'description': intervention.description,
            'status': intervention.status.value,
            'priority': intervention.priority,
            'scheduled_date': intervention.scheduled_date.isoformat(),
            'scheduled_time': intervention.scheduled_time.isoformat() if intervention.scheduled_time else None,
            'assigned_to': intervention.assigned_to.full_name() if intervention.assigned_to else None,
            'created_at': intervention.created_at.isoformat()
        }
    
    def serialize_attendance(self, attendance_records):
        """Serialize attendance records"""
        return [
            {
                'date': record.date.isoformat(),
                'status': record.status,
                'check_in_time': record.check_in_time.isoformat() if record.check_in_time else None,
                'total_minutes': record.total_minutes
            }
            for record in attendance_records
        ]
    
    def serialize_academics(self, academic_records):
        """Serialize academic records"""
        return [
            {
                'subject': record.subject,
                'assessment_type': record.assessment_type,
                'title': record.title,
                'score': record.score,
                'max_score': record.max_score,
                'percentage': record.percentage,
                'grade': record.grade,
                'date': record.date.isoformat(),
                'late_submission': record.late_submission
            }
            for record in academic_records
        ]
    
    def serialize_alerts(self, alerts):
        """Serialize alerts"""
        return [self.serialize_alert(alert) for alert in alerts]
    
    def serialize_interventions(self, interventions):
        """Serialize interventions"""
        return [self.serialize_intervention(intervention) for intervention in interventions]
    
    def serialize_performance_trend(self, trend):
        """Serialize performance trend"""
        return {
            'date': trend.date.isoformat(),
            'average_score': trend.average_score,
            'attendance_rate': trend.attendance_rate,
            'assignment_completion_rate': trend.assignment_completion_rate,
            'quiz_average': trend.quiz_average,
            'engagement_score': trend.engagement_score,
            'overall_performance_score': trend.overall_performance_score
        }
    
    def predict_ml_risk(self, risk_profile):
        """Predict risk using ML model"""
        try:
            features = np.array([[
                risk_profile.attendance_rate,
                risk_profile.average_score,
                risk_profile.behavior_score,
                risk_profile.engagement_score,
                risk_profile.attendance_factor,
                risk_profile.academic_factor,
                risk_profile.behavior_factor,
                risk_profile.engagement_factor
            ]])
            
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]
            
            return {
                'prediction': int(prediction),
                'probability': {
                    'safe': float(probability[0]),
                    'at_risk': float(probability[1])
                },
                'confidence': max(probability) * 100,
                'method': 'ml'
            }
        except Exception as e:
            logger.error(f"ML prediction error: {str(e)}")
            return self.predict_rule_based_risk(risk_profile)
    
    def predict_rule_based_risk(self, risk_profile):
        """Predict risk using rule-based logic"""
        risk_score = risk_profile.current_risk_score
        
        if risk_score >= 80:
            prediction = 1
            risk_level = 'CRITICAL'
        elif risk_score >= 60:
            prediction = 1
            risk_level = 'HIGH'
        elif risk_score >= 40:
            prediction = 0
            risk_level = 'MEDIUM'
        else:
            prediction = 0
            risk_level = 'LOW'
        
        return {
            'prediction': prediction,
            'probability': {
                'safe': 1.0 - (risk_score / 100),
                'at_risk': risk_score / 100
            },
            'confidence': 85.0,
            'method': 'rule_based',
            'risk_level': risk_level
        }
    
    def calculate_risk_factors(self, student):
        """Calculate detailed risk factors"""
        try:
            # Get recent data
            thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
            
            attendance_records = student.attendance_records.filter(Attendance.date >= thirty_days_ago).all()
            academic_records = student.academic_records.filter(AcademicRecord.date >= thirty_days_ago).all()
            
            # Calculate factors
            attendance_rate = len([r for r in attendance_records if r.status == 'Present']) / len(attendance_records) * 100 if attendance_records else 100
            average_score = sum(r.percentage for r in academic_records) / len(academic_records) if academic_records else 100
            
            return {
                'attendance_rate': attendance_rate,
                'average_score': average_score,
                'total_classes': len(attendance_records),
                'present_classes': len([r for r in attendance_records if r.status == 'Present']),
                'recent_assessments': len(academic_records),
                'performance_trend': 'stable'  # Calculate based on historical data
            }
        except Exception as e:
            logger.error(f"Error calculating risk factors: {str(e)}")
            return {}
    
    def generate_risk_recommendations(self, risk_profile, ml_prediction):
        """Generate risk-based recommendations"""
        recommendations = []
        
        if not risk_profile:
            return recommendations
        
        risk_level = risk_profile.risk_level.value if risk_profile.risk_level else 'LOW'
        
        if risk_level in ['HIGH', 'CRITICAL']:
            recommendations.extend([
                "Schedule immediate counseling session",
                "Conduct parent-teacher meeting",
                "Develop personalized improvement plan",
                "Increase monitoring frequency",
                "Consider academic support services"
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                "Schedule regular check-ins",
                "Monitor academic progress closely",
                "Provide additional study resources",
                "Encourage participation in school activities"
            ])
        else:
            recommendations.extend([
                "Continue regular monitoring",
                "Acknowledge and encourage good performance",
                "Provide enrichment opportunities"
            ])
        
        # Add ML-specific recommendations
        if ml_prediction and ml_prediction.get('confidence', 0) > 80:
            if ml_prediction['prediction'] == 1:
                recommendations.append("ML model indicates high dropout risk - immediate action recommended")
            else:
                recommendations.append("ML model indicates low risk - continue current support strategies")
        
        return recommendations
    
    def trigger_alert_notifications(self, alert):
        """Trigger background notifications for new alert"""
        try:
            # This would integrate with Celery/Redis for background jobs
            # For now, just log the alert
            logger.info(f"Alert triggered: {alert.title} for student {alert.student_id}")
            
            # TODO: Implement actual notification system
            # - Send email to assigned staff
            # - Send SMS to parents (if configured)
            # - Create in-app notification
            # - Schedule follow-up reminder
            
        except Exception as e:
            logger.error(f"Error triggering alert notifications: {str(e)}")

# Initialize API
api = EarlyWarningAPI()
