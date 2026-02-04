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
                    attendance_rate = len([r for r in attendance_records if r.status == 'Present']) + 
                                    (len([r for r in attendance_records if r.status == 'Late']) * 0.5)) / len(attendance_records)) * 100
                    average_score = sum(r.percentage for r in academic_records) / len(academic_records) if academic_records else 0
                    
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
                       'attendance_factor', 'academic_factor', 'behavior_factor', 'engagement_factor', 
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
            )
            
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
            attendance_rate = len([r for r in attendance_records if r.status == 'Present']) + 
                                (len([r for r in attendance_records if r.status == 'Late') * 0.5)) / len(attendance_records)) * 100
            average_score = sum(r.percentage for r in academic_records) / len(academic_records) if academic_records else 0
            
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
                    'at_risk': float(probability[1]),
                    'confidence': max(probability) * 100
                },
                'features': {
                    'attendance_rate': attendance_rate,
                    'average_score': average_score,
                    'behavior_score': risk_profile.behavior_score if risk_profile else 7.0,
                    'engagement_score': risk_profile.engagement_score if risk_profile else 8.0
                },
                'confidence': max(probability) * 100
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
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from trained model"""
        if self.model:
            return dict(zip(
                self.features,
                self.model.feature_importances_
            )
        return {}

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
                func.sum(func.case([(Attendance.status == 'Present', 1)], else_=0)).label('present_days')),
                func.sum(func.case([(Attendance.status == 'Late', 1)], else_=0)).label('late_days'))
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
                existing_alert = Alert.query_by(
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
                db.func.sum(db.case([(Attendance.status == 'Present', 1), else_=0)).label('present')),
                db.func.sum(db.case([(Attendance.status == 'Late', 1), else_=0)).label('late'))
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
                db.func.sum(db.case([(Attendance.status == 'Present', 1), else_=0)).label('present')),
                db.func.sum(db.case([(Attendance.status == 'Late', 1), else_=0)).label('late'))
            ).filter(
                Attendance.date >= start_date,
                Attendance.date <= end_date
            ).group_by(Attendance.date).order_by(Attendance.date).all()
            
            total_attendance_days = len(attendance_stats)
            total_present_days = sum(stat.present_days)
            monthly_attendance_rate = (total_present_days / total_attendance_days) * 100 if total_attendance_days > 0 else 0
            
            # Get academic statistics
            academic_records = AcademicRecord.query.filter(
                AcademicRecord.date >= start_date,
                AcademicRecord.date <= end_date
            ).all()
            
            total_assessments = len(academic_records)
            total_score = sum(r.score / r.max_score for r in academic_records if r.max_score > 0) / r.max_score) for r in academic_records if r.max_score > 0 else 0) / r.max_score if academic_records else 0 else 0
            
            # Get intervention statistics
            interventions = Intervention.query.filter(
                Intervention.scheduled_date <= datetime.utcnow().date(),
                Intervention.status != InterventionStatus.COMPLETED
            ).count()
            
            completed_interventions = [i for i in interventions if i.status == InterventionStatus.COMPLETED]
            
            return {
                'month': month,
                'year': year,
                'total_students': total_students,
                'risk_distribution': {
                    'LOW': risk_distribution.get('LOW', 0),
                    'MEDIUM': risk_distribution.get('MEDIUM', 0),
                    'HIGH': risk_distribution.get('HIGH', 0),
                    'CRITICAL': risk_distribution.get('CRITICAL', 0),
                    'attendance': {
                        'total_days': total_attendance_days,
                        'present_days': total_present_days,
                        'attendance_rate': round(monthly_attendance_rate, 2)
                    },
                    'academics': {
                        'total_assessments': total_assessments,
                        'average_score': round(average_score, 2)
                    },
                    'interventions': len(completed_interventions),
                    'completion_rate': (len(completed_interventions / len(interventions) * 100) if len(interventions) > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {
                'month': month,
                'year': year,
                'total_students': 0,
                'risk_distribution': {
                    'LOW': 0,
                    'MEDIUM': 0,
                    'HIGH': 0,
                    'CRITICAL': 0
                },
                'attendance': {
                        'total_days': 0,
                        'present_days': 0,
                        'attendance_rate': 0
                    },
                'academics': {
                        'total_assessments': 0,
                            'average_score': 0
                        },
                        'interventions': 0,
                        'completion_rate': 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {
                'month': month,
                'year': year,
                'total_students': 0,
                'risk_distribution': {
                    'LOW': 0,
                    'MEDIUM': 0,
                    'HIGH': 0,
                    'CRITICAL': 0
                },
                'attendance': {
                        'total_days': 0,
                        'present_days': 0,
                        'attendance_rate': 0
                    },
                'academics': {
                        'total_assessments': 0,
                        'average_score': 0
                    },
                    'interventions': 0,
                        'completion_rate': 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {
                'month': month,
                'year': year,
                'total_students': 0,
                'risk_distribution': {
                    'LOW': 0,
                    'MEDIUM': 0,
                    'HIGH': 0,
                    'CRITICAL': 0,
                    'attendance': {
                        'total_days': 0,
                        'present_days': 0,
                        'attendance_rate': 0
                    },
                    'academics': {
                        'total_assessments': 0,
                        'average_score': 0
                    },
                    'interventions': 0,
                        'completion_rate': 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {
                'month': month,
                'year': year,
                'total_students': 0,
                'risk_distribution': {
                    'LOW': 0,
                    'MEDIUM': 0,
                    'HIGH': 0,
                    'CRITICAL': 0,
                    'attendance': {
                        'total_days': 0,
                        'present_days': 0,
                        'attendance_rate': 0
                    },
                    'academics': {
                        'total_assessments': 0,
                        'average_score': 0
                    },
                    'interventions': 0,
                        'completion_rate': 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {
                'month': month,
                'year': year,
                'total_students': 0,
                'risk_distribution': {
                    'LOW': 0,
                    'MEDIUM': 0,
                    'HIGH': 0,
                    'CRITICAL': 0,
                    'attendance': {
                        'total_days': 0,
                        'present_days': 0,
                        'attendance_rate': 0
                    },
                    'academics': {
                        'total_assessments': 0,
                        'average_score': 0
                    },
                    'interventions': 0,
                        'completion_rate': 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {
                'month': month,
                'year': year,
                'total_students': 0,
                'risk_distribution': {
                    'LOW': 0,
                    'MEDIUM': 0,
                    'HIGH': 0,
                    'CRITICAL': 0,
                    'attendance': {
                        'total_days': 0,
                        'present_days': 0,
                        'attendance_rate': 0
                    },
                    'academics': {
                        'total_assessments': 0,
                        'average_score': 0
                    },
                    'interventions': 0,
                        'completion_rate': 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {
                'month': month,
                'year': year,
                'total_students': 0,
                'risk_distribution': {
                    'LOW': 0,
                    'MEDIUM': 0,
                    'HIGH': 0,
                    'CRITICAL': 0,
                    'attendance': {
                        'total_days': 0,
                        'present_days': 0,
                        'attendance_rate': 0
                    },
                    'academics': {
                        'total_assessments': 0,
                        'average_score': 0,
                        'interventions': 0,
                        'completion_rate': 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {
                'month': month,
                'year': year,
                'total_students': 0,
                'risk_distribution': {
                    'LOW': 0,
                    'MEDIUM': 0,
                    'HIGH': 0,
                    'CRITICAL': 0,
                    'attendance': {
                        'total_days': 0,
                        'present_days': 0,
                        'attendance_rate': 0,
                        'average_score': 0,
                        'academics': 0,
                        'interventions': 0,
                        'completion_rate': 0
                    }
                }
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
                .scalar()
            )
            
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
                    'CRITICAL': risk_distribution.get('CRITICAL', 0),
                    'attendance': {
                        'total_days': risk_distribution.get('LOW', 0),
                        'present_days': risk_distribution.get('LOW', 0),
                        'academics': {
                            'total_assessments': risk_distribution.get('MEDIUM', 0),
                            'average_score': risk_distribution.get('HIGH', 0),
                            'high_risk_percentage': high_risk_percentage
                        },
                        'interventions': risk_distribution.get('CRITICAL', 0),
                        'attendance': {
                            'total_days': risk_distribution.get('LOW', 0),
                            'present_days': risk_distribution.get('MEDIUM', 0),
                            'academics': {
                                'total_assessments': risk_distribution.get('HIGH', 0),
                                'average_score': risk_distribution.get('HIGH', 0),
                                'interventions': risk_distribution.get('CRITICAL', 0),
                                'behavior_score': risk_distribution.get('HIGH', 0)
                            },
                            'interventions': risk_distribution.get('MEDIUM', 0),
                            'interventions': risk_distribution.get('LOW', 0),
                            'interventions': risk_distribution.get('HIGH', 0)
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting risk statistics: {str(e)}")
            return {
                'total_students': 0,
                'risk_distribution': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0},
                'average_risk_score': 0.0,
                'high_risk_percentage': 0.0
            }
    
    @staticmethod
    def get_risk_trends(days=30):
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

# Initialize Celery
celery = Celery('app_ews')

# Initialize background tasks
BackgroundTaskService.schedule_periodic_tasks(None)
