"""
Enhanced Services for Early Warning System (EWS)
ML Integration, Background Tasks, and Business Logic
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import logging
from typing import Dict, List, Optional, Tuple
import json
import asyncio
import threading
from celery import Celery
from models_ews import db, Student, RiskProfile, Alert, Intervention, Attendance, AcademicRecord, RiskLevel, AlertType, AlertStatus, InterventionStatus, PerformanceTrend, EngagementMetric, User
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import joinedload
import os

logger = logging.getLogger(__name__)

# Initialize Celery
celery = Celery('app_ews')

class MLService:
    """Machine Learning Service for Risk Prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = None
        self.model_path = os.environ.get('ML_MODEL_PATH', 'model/model.pkl')
        self.scaler_path = os.environ.get('ML_SCALER_PATH', 'model/scaler.pkl')
        self.features_path = os.environ.get('ML_FEATURES_PATH', 'model/features.pkl')
        self.load_model()
    
    def load_model(self):
        """Load trained ML model"""
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            self.features = joblib.load(self.features_path)
            logger.info("ML model loaded successfully")
        except FileNotFoundError:
            logger.warning("ML model not found. Please train the model first.")
            self.model = None
            self.scaler = None
            self.features = None
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Prepare data for ML training"""
        try:
            # Get all students with their data
            students = Student.query.all()
            
            training_data = []
            
            for student in students:
                # Get attendance data (last 30 days)
                thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
                attendance_records = student.attendance_records.filter(
                    Attendance.date >= thirty_days_ago
                ).all()
                
                # Get academic records
                academic_records = student.academic_records.filter(
                    AcademicRecord.date >= thirty_days_ago
                ).all()
                
                # Get performance trends
                performance_trends = student.performance_trends.filter(
                    PerformanceTrend.date >= thirty_days_ago
                ).order_by(PerformanceTrend.date.desc()).all()
                
                # Get engagement metrics
                engagement_metrics = student.engagement_metrics.filter(
                    EngagementMetric.date >= thirty_days_ago
                ).order_by(EngagementMetric.date.desc()).all()
                
                # Calculate features
                if attendance_records and academic_records:
                    attendance_rate = len([r for r in attendance_records if r.status == 'Present']) / len(attendance_records) * 100
                    average_score = sum(r.percentage for r in academic_records) / len(academic_records)
                    
                    # Get latest risk profile
                    risk_profile = student.current_risk_profile()
                    
                    # Create feature vector
                    features = [
                        attendance_rate,
                        average_score,
                        risk_profile.behavior_score if risk_profile else 7.0,
                        risk_profile.engagement_score if risk_profile else 8.0,
                        risk_profile.attendance_factor if risk_profile else 0.0,
                        risk_profile.academic_factor if risk_profile else 0.0,
                        risk_profile.behavior_factor if risk_profile else 0.0,
                        risk_profile.engagement_factor if risk_profile else 0.0
                    ]
                    
                    # Get target (dropout status)
                    target = 1 if risk_profile and risk_profile.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else 0
                    
                    training_data.append({
                        'student_id': student.id,
                        'features': features,
                        'target': target,
                        'attendance_rate': attendance_rate,
                        'average_score': average_score,
                        'risk_score': risk_profile.current_risk_score if risk_profile else 0.0
                    })
            
            df = pd.DataFrame(training_data)
            
            # Split features and target
            X = df[['attendance_rate', 'average_score', 'behavior_score', 'engagement_score', 
                       'attendance_factor', 'academic_factor', 'behavior_factor', 'engagement_factor'])
            y = df['target']
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return pd.DataFrame(), pd.Series()
    
    def train_model(self) -> Dict:
        """Train the ML model"""
        try:
            X, y = self.prepare_training_data()
            
            if len(X) == 0:
                return {
                    'success': False,
                    'error': 'No training data available'
                }
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(['attendance_rate', 'average_score', 'behavior_score', 'engagement_score', 
                        'attendance_factor', 'academic_factor', 'behavior_factor', 'engagement_factor'], 
                        self.features_path)
            
            # Get feature importance
            feature_importance = dict(zip(
                ['attendance_rate', 'average_score', 'behavior_score', 'engagement_score', 
                         'attendance_factor', 'academic_factor', 'behavior_factor', 'engagement_factor'],
                self.model.feature_importances_
            ))
            
            logger.info(f"Model trained successfully with accuracy: {accuracy:.4f}")
            
            return {
                'success': True,
                'accuracy': accuracy,
                'model_path': self.model_path,
                'feature_importance': feature_importance,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def predict_risk(self, student_id: int) -> Dict:
        """Predict risk for a specific student"""
        try:
            if not self.model:
                return {
                    'success': False,
                    'error': 'ML model not available'
                }
            
            student = Student.query.get(student_id)
            if not student:
                return {
                    'success': False,
                    'error': 'Student not found'
                }
            
            # Get student data
            thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
            attendance_records = student.attendance_records.filter(
                Attendance.date >= thirty_days_ago
            ).all()
            
            academic_records = student.academic_records.filter(
                AcademicRecord.date >= thirty_days_ago
            ).all()
            
            performance_trends = student.performance_trends.filter(
                PerformanceTrend.date >= thirty_days_ago
            ).order_by(PerformanceTrend.date.desc()).all()
            
            engagement_metrics = student.engagement_metrics.filter(
                EngagementMetric.date >= thirty_days_ago
            ).order_by(EngagementMetric.date.desc()).all()
            
            # Calculate features
            attendance_rate = len([r for r in attendance_records if r.status == 'Present']) / len(attendance_records) * 100
            average_score = sum(r.percentage for r in academic_records) / len(academic_records)
            
            risk_profile = student.current_risk_profile()
            
            features = np.array([[
                attendance_rate,
                average_score,
                risk_profile.behavior_score if risk_profile else 7.0,
                risk_profile.engagement_score if risk_profile else 8.0,
                risk_profile.attendance_factor if risk_profile else 0.0,
                risk_profile.academic_factor if risk_profile else 0.0,
                risk_profile.behavior_factor if risk_profile else 0.0,
                risk_profile.engagement_factor if risk_profile else 0.0
            ]).reshape(1, -1)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]
            
            return {
                'success': True,
                'prediction': int(prediction),
                'probability': {
                    'safe': float(probability[0]),
                    'at_risk': float(probability[1])
                },
                'confidence': max(probability) * 100,
                'features': {
                    'attendance_rate': attendance_rate,
                    'average_score': average_score,
                    'behavior_score': risk_profile.behavior_score if risk_profile else 7.0,
                    'engagement_score': risk_profile.engagement_score if risk_profile else 8.0
                }
            }
            
        except Exception as e:
            logger.error(f"Error predicting risk for student {student_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_predict_risk(self, student_ids: List[int] = None) -> Dict:
        """Batch predict risk for multiple students"""
        try:
            if student_ids is None:
                students = Student.query.all()
                student_ids = [s.id for s in students]
            
            results = []
            for student_id in student_ids:
                result = self.predict_risk(student_id)
                results.append({
                    'student_id': student_id,
                    **result
                })
            
            return {
                'success': True,
                'predictions': results
            }
            
        except Exception as e:
            logger.error(f"Error in batch risk prediction: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'predictions': []
            }

class BackgroundTaskService:
    """Background Task Service for Scheduled Jobs"""
    
    @staticmethod
    @celery.task
    def assess_student_risks():
        """Assess risks for all students"""
        try:
            from services_ews.risk_service import RiskCalculationService
            
            logger.info("Starting risk assessment for all students")
            result = RiskCalculationService.batch_update_risk_scores()
            
            logger.info(f"Risk assessment completed: {result}")
            
            # Trigger alerts for high-risk students
            if result['high_risk_students'] > 0:
                BackgroundTaskService.trigger_high_risk_alerts(result['high_risk_students'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error in risk assessment task: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    @celery.task
    def check_attendance_alerts():
        """Check for attendance-related alerts"""
        try:
            logger.info("Checking attendance alerts")
            
            # Get students with low attendance in the last 7 days
            seven_days_ago = datetime.utcnow().date() - timedelta(days=7)
            
            low_attendance_students = db.session.query(
                Student.id,
                func.count(Attendance.id).label('total_days'),
                func.sum(db.case([(Attendance.status == 'Present', 1)], else_=0)).label('present_days')
            ).join(Attendance).filter(
                Attendance.date >= seven_days_ago
            ).group_by(Student.id).having(
                func.count(Attendance.id) > 0)
            ).all()
            
            alerts_created = 0
            
            for student_data in low_attendance_students:
                attendance_rate = (student_data.present_days / student_data.total_days) * 100
                
                if attendance_rate < 75: # Alert threshold
                    # Check if alert already exists
                    existing_alert = Alert.query.filter_by(
                        student_id=student_data.id,
                        type=AlertType.ATTENDANCE_DECLINE,
                        status=AlertStatus.ACTIVE
                    ).first()
                    
                    if not existing_alert:
                        alert = Alert(
                        student_id=student_data.id,
                        type=AlertType.ATTENDANCE_DECLINE,
                        title=f"Low Attendance Alert - {student_data.student_id}",
                        message=f"Student's attendance is {attendance_rate:.1f}% which is below the 75% threshold",
                        risk_score=100 - attendance_rate,
                        created_by=1  # Admin user
                    )
                        db.session.add(alert)
                        alerts_created += 1
            
            db.session.commit()
            logger.info(f"Created {alerts_created} attendance alerts")
            
            return {
                'success': True,
                'alerts_created': alerts_created
            }
            
        except Exception as e:
            logger.error(f"Error in attendance alert task: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    @celery.task
    def check_performance_alerts():
        """Check for performance-related alerts"""
        try:
            logger.info("Checking performance alerts")
            
            # Get students with declining performance
            seven_days_ago = datetime.utcnow().date() - timedelta(days=7)
            
            declining_students = db.session.query(
                Student.id,
                func.avg(AcademicRecord.percentage).label('avg_percentage')
            ).join(AcademicRecord).filter(
                AcademicRecord.date >= seven_days_ago
            ).group_by(Student.id).having(
                func.avg(AcademicRecord.percentage) < 60
            ).all()
            
            alerts_created = 0
            
            for student_data in declining_students:
                avg_percentage = student_data.avg_percentage
                
                # Check if alert already exists
                existing_alert = Alert.query.filter_by(
                    student_id=student_data.id,
                    type=AlertType.PERFORMANCE_DROP,
                    status=AlertStatus.ACTIVE
                ).first()
                
                if not existing_alert:
                    alert = Alert(
                        student_id=student_data.id,
                        type=AlertType.PERFORMANCE_DROP,
                        title=f"Performance Drop Alert - {student_data.student_id}",
                        message=f"Student's average score is {avg_percentage:.1f}% which is below the 60% threshold",
                        risk_score=100 - avg_percentage,
                        created_by=1  # Admin user
                    )
                    db.session.add(alert)
                    alerts_created += 1
            
            db.session.commit()
            logger.info(f"Created {alerts_created} performance alerts")
            
            return {
                'success': True,
                'alerts_created': alerts_created
            }
            
        except Exception as e:
            logger.error(f"Error in performance alert task: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def trigger_high_risk_students(high_risk_students):
        """Trigger alerts for high-risk students"""
        try:
            for student_id in high_risk_students:
                # Check if alert already exists
                existing_alert = Alert.query.filter_by(
                    student_id=student_id,
                    type=AlertType.HIGH_RISK,
                    status=AlertStatus.ACTIVE
                ).first()
                
                if not existing_alert:
                    student = Student.query.get(student_id)
                    
                    alert = Alert(
                        student_id=student_id,
                        type=AlertType.HIGH_RISK,
                        title=f"High Risk Alert - {student.full_name()}",
                        message=f"Student has been identified as high risk for dropout. Immediate intervention recommended.",
                        risk_score=85.0,
                        created_by=1
                    )
                    db.session.add(alert)
            
            db.session.commit()
            logger.info(f"Triggered alerts for {len(high_risk_students)} high-risk students")
            
        except Exception as e:
            logger.error(f"Error triggering high-risk alerts: {str(e)}")
    
    @staticmethod
    def schedule_periodic_tasks(app):
        """Schedule periodic background tasks"""
        # Schedule risk assessment every 24 hours
        celery.send_task('services_ews.background_tasks.BackgroundTaskService.assess_student_risks', 
                         countdown=24*60*60) # 24 hours
        
        # Schedule attendance checks every hour
        celery.send_task('services_ews.background_tasks.BackgroundTaskService.check_attendance_alerts', 
                         countdown=60*60) # 1 hour
        
        # Schedule performance checks every 6 hours
        celery.send_task('services_ews.background_tasks.BackgroundTaskService.check_performance_alerts', 
                         countdown=6*60*60) 6 hours)

class RiskCalculationService:
    """Enhanced Risk Calculation Service"""
    
    @staticmethod
    def calculate_student_risk(student_id: int) -> RiskProfile:
        """Calculate comprehensive risk score for a student"""
        try:
            student = Student.query.get(student_id)
            if not student:
                raise ValueError(f"Student not found: {student_id}")
            
            # Get data for last 30 days
            thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
            
            attendance_records = student.attendance_records.filter(
                Attendance.date >= thirty_days_ago
            ).all()
            
            academic_records = student.academic_records.filter(
                AcademicRecord.date >= thirty_days_ago
            ).all()
            
            performance_trends = student.performance_trends.filter(
                PerformanceTrend.date >= thirty_days_ago
            ).order_by(PerformanceTrend.date.desc()).all()
            
            engagement_metrics = student.engagement_metrics.filter(
                EngagementMetric.date >= thirty_days_ago
            ).order_by(EngagementMetric.date.desc()).all()
            
            # Calculate attendance metrics
            if attendance_records:
                total_days = len(attendance_records)
                present_days = len([r for r in attendance_records if r.status == 'Present']) + 
                                (len([r for r in attendance_records if r.status == 'Late']) * 0.5)) / total_days) * 100
            else:
                attendance_rate = 100.0
            
            # Calculate academic metrics
            if academic_records:
                total_percentage = sum(r.percentage for r in academic_records)
                average_score = total_percentage / len(academic_records) if academic_records > 0 else 100.0
            
            # Calculate engagement metrics
            if engagement_metrics:
                avg_engagement_score = sum(m.engagement_score for m in engagement_metrics) / len(engagement_metrics)
                lms_login_count = sum(m.lms_login_count for m in engagement_metrics)
                avg_time_spent = sum(m.time_spent_minutes for m in engagement_metrics)
            else:
                avg_engagement_score = 8.0
                lms_login_count = 0
                avg_time_spent = 0
            
            # Calculate behavioral metrics
            risk_profile = student.current_risk_profile()
            behavior_score = risk_profile.behavior_score if risk_profile else 7.0
            
            # Calculate risk factors
            attendance_factor = max(0, 100 - attendance_rate) * 0.4)
            academic_factor = max(0, 100 - average_score) * 0.4)
            behavior_factor = max(0, (10 - behavior_score * 10) * 0.2)
            engagement_factor = max(0, (10 - avg_engagement_score * 10) * 0.2)
            
            # Calculate trend factors
            trend_factor = 0.0
            if len(performance_trends) >= 2):
                recent_avg = sum(p.overall_performance_score for p in performance_trends[:2]) / 2
                older_avg = sum(p.overall_performance_score for p in performance_trends[2:]) / len(performance_trends[2:]) if len(performance_trends) > 2 else recent_avg)
                
                if recent_avg < older_avg - 5:
                    trend_factor = 10.0
                elif recent_avg > older_avg + 5:
                    trend_factor = -10.0
                else:
                    trend_factor = 0.0
            
            # Calculate weighted risk score
            risk_score = (attendance_factor * 0.4) + (academic_factor * 0.4) + (behavior_factor * 0.1) + (engagement_factor * 0.1) + (trend_factor * 0.0)
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 60:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 40:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Apply critical overrides
            if attendance_rate < 60:
                risk_level = RiskLevel.CRITICAL
                risk_score = max(risk_score, 85.0)
            elif average_score < 40:
                risk_level = RiskLevel.HIGH
                risk_score = max(risk_score, 80.0)
            
            # Update or create risk profile
            risk_profile = student.risk_profile
            if not risk_profile:
                risk_profile = RiskProfile(student_id=student_id)
                db.session.add(risk_profile)
            
            risk_profile.current_risk_score = round(risk_score, 2)
            risk_profile.risk_level = risk_level
            risk_profile.attendance_factor = round(attendance_factor, 2)
            risk_profile.academic_factor = round(academic_factor, 2)
            risk_profile.behavior_factor = round(behavior_factor, 2)
            risk_profile.engagement_factor = round(engagement_factor, 2)
            risk_profile.attendance_rate = round(attendance_rate, 2)
            risk_profile.average_score = round(average_score, 2)
            risk_profile.behavior_score = behavior_score
            risk_profile.engagement_score = avg_engagement_score
            risk_profile.last_updated = datetime.utcnow()
            risk_profile.created_at = datetime.utcnow()
            risk_profile.updated_at = datetime.utcnow()
            
            # Update risk trend
            previous_risk_score = risk_profile.previous_risk_score
            if previous_risk_score:
                if risk_score > previous_risk_score + 5:
                    risk_profile.risk_trend = 'Declining'
                elif risk_score < previous_risk_score - 5:
                    risk_profile.risk_trend = 'Improving'
                else:
                    risk_profile.risk_trend = 'Stable'
            
            risk_profile.previous_risk_score = risk_score
            
            db.session.commit()
            
            logger.info(f"Risk calculated for student {student.full_name()}: {risk_level.value} ({risk_score:.2f})")
            
            return risk_profile
            
        except Exception as e:
            logger.error(f"Error calculating risk for student {student_id}: {str(e)}")
            raise
    
    @staticmethod
    def batch_update_risk_scores(student_ids: List[int] = None) -> Dict:
        """Update risk scores for multiple students"""
        try:
            if student_ids is None:
                students = Student.query.all()
                student_ids = [s.id for s in students]
            
            updated_count = 0
            failed_count = 0
            errors = []
            
            for student_id in student_ids:
                try:
                    RiskCalculationService.calculate_student_risk(student_id)
                    updated_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Student {student_id}: {str(e)}")
            
            return {
                'total_students': len(student_ids),
                'updated_count': updated_count,
                'failed_count': failed_count,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Error in batch risk update: {str(e)}")
            return {
                'total_students': 0,
                'updated_count': 0,
                'failed_count': 0,
                'errors': [str(e)]
            }
    
    @staticmethod
    def get_risk_statistics() -> Dict:
        """Get overall risk statistics"""
        try:
            total_students = Student.query.count()
            
            if total_students == 0:
                return {
                    'total_students': 0,
                    'risk_distribution': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0},
                    'average_risk_score': 0.0,
                    'high_risk_percentage': 0.0
                }
            
            # Get risk distribution
            risk_distribution = db.session.query(
                RiskProfile.risk_level,
                db.func.count(RiskProfile.id).label('count')
            ).group_by(RiskProfile.risk_level).all()
            
            # Calculate average risk score
            avg_risk_score = db.session.query(
                db.func.avg(RiskProfile.current_risk_score)
            ).scalar()
            
            # Get high risk percentage
            high_risk_count = db.session.query(
                RiskProfile.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
            ).count()
            high_risk_percentage = (high_risk_count / total_students) * 100
            
            return {
                'total_students': total_students,
                'risk_distribution': {
                    'LOW': risk_distribution.get('LOW', 0),
                    'MEDIUM': risk_distribution.get('MEDIUM', 0),
                    'HIGH': risk_distribution.get('HIGH', 0),
                    'CRITICAL': risk_distribution.get('CRITICAL', 0)
                },
                'average_risk_score': round(avg_risk_score, 2),
                'high_risk_percentage': round(high_risk_percentage, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting risk statistics: {str(e)}")
            return {
                'total_students': 0,
                'risk_distribution': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0},
                'average_risk_score': 0.0,
                'high_risk_percentage': 0.0
            }

class NotificationService:
    """Notification Service for sending alerts and notifications"""
    
    @staticmethod
    def send_email_notification(to_email, subject, message, template=None):
        """Send email notification"""
        try:
            from flask import current_app
            from flask_mail import Message
            
            if template:
                # Use email template
                msg = Message(
                    subject=subject,
                    recipients=[to_email],
                    html=message,
                    sender=current_app.config.get('MAIL_DEFAULT_SENDER')
                )
            else:
                # Plain text email
                msg = Message(
                    subject=subject,
                    recipients=[to_email],
                    body=message,
                    sender=current_app.config.get('MAIL_DEFAULT_SENDER')
                )
            
            mail.send(msg)
            logger.info(f"Email sent to {to_email}: {subject}")
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
    
    @staticmethod
    def send_sms_notification(phone_number, message):
        """Send SMS notification"""
        try:
            # Implementation would depend on SMS provider
            # This is a placeholder for SMS functionality
            logger.info(f"SMS sent to {phone_number}: {message}")
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")

class AnalyticsService:
    """Analytics Service for reporting and insights"""
    
    @staticmethod
    def get_attendance_trends(days=30):
        """Get attendance trends for specified period"""
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            trends = db.session.query(
                db.func.date(Attendance.date).label('date'),
                db.func.count(Attendance.id).label('total'),
                db.func.sum(db.case([(Attendance.status == 'Present', 1)], else_=0)).label('present'),
                db.func.sum(db.case([(Attendance.status == 'Late', 1)], else_=0)).label('late')
            ).filter(
                Attendance.date >= start_date,
                Attendance.date <= end_date
            ).group_by(Attendance.date).order_by(Attendance.date).all()
            
            return [
                {
                    'date': str(trend.date),
                    'total': trend.total,
                    'present': trend.present,
                    'late': trend.late,
                    'absent': trend.total - trend.present - trend.late,
                    'attendance_rate': round((trend.present + (trend.late * 0.5)) / trend.total) * 100, 2)
                }
                for trend in trends
            ]
            
        except Exception as e:
            logger.error(f"Error getting attendance trends: {str(e)}")
            return []
    
    @staticmethod
    def get_performance_trends(days=30):
        """Get performance trends for specified period"""
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            trends = db.session.query(
                db.func.date(PerformanceTrend.date).label('date'),
                db.func.avg(PerformanceTrend.overall_performance_score).label('avg_score'),
                db.func.avg(PerformanceTrend.attendance_rate).label('avg_attendance'),
                db.func.avg(PerformanceTrend.engagement_score).label('avg_engagement')
            ).filter(
                PerformanceTrend.date >= start_date,
                PerformanceTrend.date <= end_date
            ).group_by(PerformanceTrend.date).order_by(PerformanceTrend.date).all()
            
            return [
                {
                    'date': str(trend.date),
                    'avg_score': trend.avg_score,
                    'avg_attendance': trend.avg_attendance,
                    'avg_engagement': trend.avg_engagement,
                    'overall_performance_score': trend.overall_performance_score
                }
                for trend in trends
            ]
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {str(e)}")
            return []
    
    @staticmethod
    def get_monthly_report(month=None, year=None):
        """Generate monthly report"""
        try:
            if not month:
                month = datetime.utcnow().month
            if not year:
                year = datetime.utcnow().year
            
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            # Get student statistics
            total_students = Student.query.count()
            
            # Get risk distribution
            risk_distribution = db.session.query(
                RiskProfile.risk_level,
                db.func.count(RiskProfile.id).label('count')
            ).group_by(RiskProfile.risk_level).all()
            
            # Get attendance statistics
            attendance_stats = db.session.query(
                db.func.date(Attendance.date).label('date'),
                db.func.count(Attendance.id).label('total'),
                db.func.sum(db.case([(Attendance.status == 'Present', 1), else_=0)).label('present')
            ).filter(
                Attendance.date >= start_date,
                Attendance.date <= end_date
            ).group_by(Attendance.date).order_by(Attendance.date).all()
            
            total_attendance_days = len(attendance_stats)
            total_present_days = sum(stat.present for stat in attendance_stats)
            monthly_attendance_rate = (total_present_days / total_attendance_days * 100) if total_attendance_days > 0 else 0
            
            # Get academic statistics
            academic_records = AcademicRecord.query.filter(
                AcademicRecord.date >= start_date,
                AcademicRecord.date <= end_date
            ).all()
            
            total_assessments = len(academic_records)
            total_score = sum(r.score for r in academic_records) / total_assessments if total_assessments > 0 else 0
            
            # Get intervention statistics
            interventions = Intervention.query.filter(
                Intervention.scheduled_date >= start_date,
                Intervention.scheduled_date <= end_date
            ).all()
            
            completed_interventions = [i for i in interventions if i.status == InterventionStatus.COMPLETED]
            
            return {
                'month': month,
                'year': year,
                'total_students': total_students,
                'risk_distribution': {
                    'LOW': risk_distribution.get('LOW', 0),
                    'MEDIUM': risk_distribution.get('MEDIUM', 0),
                    'HIGH': risk_distribution.get('HIGH', 0),
                    'CRITICAL': risk_distribution.get('CRITICAL', 0)
                },
                'attendance': {
                    'total_days': total_attendance_days,
                    'present_days': total_present_days,
                    'attendance_rate': round(monthly_attendance_rate, 2)
                },
                'academics': {
                    'total_assessments': total_assessments,
                    'average_score': round(average_score, 2)
                },
                'interventions': {
                    'total_interventions': len(interventions),
                    'completed_interventions': len(completed_interventions),
                    'completion_rate': (len(completed_interventions / len(interventions) * 100) if len(interventions) > 0 else 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {}

class DataExportService:
    """Service for exporting data in various formats"""
    
    @staticmethod
    def export_students_to_csv(student_ids=None, filters=None):
        """Export student data to CSV"""
        try:
            query = Student.query()
            
            # Apply filters
            if student_ids:
                query = query.filter(Student.id.in_(student_ids))
            
            if filters:
                if filters.get('grade'):
                    query = query.filter(Student.grade == filters['grade'])
                if filters.get('risk_level'):
                    query = query.join(RiskProfile).filter(Risk_profile.risk_level == filters['risk_level'])
            
            students = query.all()
            
            # Prepare CSV data
            csv_data = []
            for student in students:
                risk_profile = student.current_risk_profile()
                
                csv_data.append({
                    'Student ID': student.student_id,
                    'First Name': student.first_name,
                    'Last Name': student.last_name,
                    'Email': student.email,
                    'Phone': student.phone,
                    'Grade': student.grade,
                    'Section': student.section,
                    'Enrollment Date': student.enrollment_date.isoformat() if student.enrollment_date else '',
                    'Risk Level': risk_profile.risk_level.value if risk_profile else 'LOW',
                    'Risk Score': risk_profile.current_risk_score if risk_profile else 0.0,
                    'Attendance Rate': risk_profile.attendance_rate if risk_profile else 100.0,
                    'Average Score': risk_profile.average_score if risk_profile else 100.0,
                    'Behavior Score': risk_profile.behavior_score if risk_profile else 7.0,
                    'Engagement Score': risk_profile.engagement_score if risk_profile else 8.0,
                    'Risk Trend': risk_profile.risk_trend if risk_profile else 'Stable',
                    'Last Updated': risk_profile.last_updated.isoformat() if risk_profile else ''
                })
            
            return csv_data
            
        except Exception as e:
            logger.error(f"Error exporting students to CSV: {str(e)}")
            return []

# Initialize Celery
celery = Celery('app_ews')

# Initialize Celery
celery = Celery('app_ews')

# Initialize background tasks
BackgroundTaskService.schedule_periodic_tasks(None)
