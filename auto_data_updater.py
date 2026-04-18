#!/usr/bin/env python3
"""
Automatic Daily Data Update System for EduGuard
Runs scheduled tasks to update student data and risk assessments
"""

import schedule
import time
import logging
from datetime import datetime, date, timedelta
from models import db, Student, RiskProfile, Attendance, Alert
from enhanced_ai_predictor import EnhancedRiskPredictor
from services.ml_service import ml_service
from app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDataUpdater:
    """Handles automatic daily updates of student data"""
    
    def __init__(self):
        self.app = create_app()
        self.predictor = EnhancedRiskPredictor()
        
    def run_daily_updates(self):
        """Run all daily update tasks"""
        logger.info("Starting daily data updates...")
        
        with self.app.app_context():
            try:
                # Update attendance data
                self.update_attendance_records()
                
                # Update risk assessments
                self.update_risk_assessments()
                
                # Generate new alerts
                self.generate_daily_alerts()
                
                # Update AI predictions
                self.update_ai_predictions()
                
                # Clean up old data
                self.cleanup_old_data()
                
                logger.info("Daily updates completed successfully!")
                
            except Exception as e:
                logger.error(f"Error during daily updates: {e}")
    
    def update_attendance_records(self):
        """Update attendance records and calculate rates"""
        logger.info("Updating attendance records...")
        
        students = Student.query.all()
        updated_count = 0
        
        for student in students:
            try:
                # Calculate attendance rate for last 30 days
                thirty_days_ago = date.today() - timedelta(days=30)
                recent_attendance = Attendance.query.filter(
                    Attendance.student_id == student.id,
                    Attendance.date >= thirty_days_ago
                ).all()
                
                if recent_attendance:
                    present_count = len([a for a in recent_attendance if a.status == 'Present'])
                    attendance_rate = (present_count / len(recent_attendance)) * 100
                else:
                    attendance_rate = 85.0  # Default if no records
                
                # Update risk profile
                risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
                if risk_profile:
                    risk_profile.attendance_rate = attendance_rate
                    updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating attendance for student {student.id}: {e}")
        
        logger.info(f"Updated attendance for {updated_count} students")
    
    def update_risk_assessments(self):
        """Update risk assessments for all students"""
        logger.info("Updating risk assessments...")
        
        students = Student.query.all()
        updated_count = 0
        
        for student in students:
            try:
                risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
                if not risk_profile:
                    risk_profile = RiskProfile(student_id=student.id)
                    db.session.add(risk_profile)
                
                # Update risk score using holistic model
                risk_profile.update_risk_score()
                
                # Add ML prediction if available
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
                    logger.warning(f"ML prediction failed for student {student.id}: {ml_err}")
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating risk assessment for student {student.id}: {e}")
        
        db.session.commit()
        logger.info(f"Updated risk assessments for {updated_count} students")
    
    def generate_daily_alerts(self):
        """Generate daily alerts based on risk assessments"""
        logger.info("Generating daily alerts...")
        
        # Get students with high or critical risk
        at_risk_students = Student.query.join(RiskProfile).filter(
            RiskProfile.risk_level.in_(['High', 'Critical'])
        ).all()
        
        alerts_created = 0
        
        for student in at_risk_students:
            try:
                risk_profile = student.risk_profile
                
                # Check if active alert already exists
                existing_alert = Alert.query.filter_by(
                    student_id=student.id,
                    status='Active',
                    alert_type='Risk Level'
                ).first()
                
                if not existing_alert:
                    # Create new alert
                    alert = Alert(
                        student_id=student.id,
                        alert_type='Risk Level',
                        severity=risk_profile.risk_level,
                        title=f'{risk_profile.risk_level} Risk Detected - {student.first_name} {student.last_name}',
                        description=f'Risk score: {risk_profile.risk_score:.1f}. Key factors: Attendance: {risk_profile.attendance_rate:.1f}%, Academic: {risk_profile.academic_performance:.1f}%',
                        status='Active'
                    )
                    db.session.add(alert)
                    alerts_created += 1
                
                # Generate attendance alerts if needed
                if risk_profile.attendance_rate and risk_profile.attendance_rate < 60:
                    attendance_alert = Alert.query.filter_by(
                        student_id=student.id,
                        alert_type='Attendance',
                        status='Active'
                    ).first()
                    
                    if not attendance_alert:
                        attendance_alert = Alert(
                            student_id=student.id,
                            alert_type='Attendance',
                            severity='Critical' if risk_profile.attendance_rate < 50 else 'High',
                            title=f'Critical Attendance Issue - {student.first_name} {student.last_name}',
                            description=f'Attendance rate: {risk_profile.attendance_rate:.1f}% (Below 60% threshold)',
                            status='Active'
                        )
                        db.session.add(attendance_alert)
                        alerts_created += 1
                
            except Exception as e:
                logger.error(f"Error generating alerts for student {student.id}: {e}")
        
        db.session.commit()
        logger.info(f"Generated {alerts_created} new alerts")
    
    def update_ai_predictions(self):
        """Update AI predictions for all students"""
        logger.info("Updating AI predictions...")
        
        students = Student.query.all()
        updated_count = 0
        
        for student in students:
            try:
                # Prepare student data for AI prediction
                student_data = {
                    'gpa': student.gpa or 0,
                    'attendance_rate': student.risk_profile.attendance_rate if student.risk_profile else 85,
                    'academic_performance': student.risk_profile.academic_performance if student.risk_profile else 75,
                    'credits_completed': student.credits_completed or 0,
                    'year': student.year or 1,
                    'semester': student.semester or 1,
                    'financial_issues': student.risk_profile.financial_issues if student.risk_profile else False,
                    'family_problems': student.risk_profile.family_problems if student.risk_profile else False,
                    'health_issues': student.risk_profile.health_issues if student.risk_profile else False,
                    'social_isolation': student.risk_profile.social_isolation if student.risk_profile else False,
                    'mental_wellbeing_score': student.risk_profile.mental_wellbeing_score if student.risk_profile else 8
                }
                
                # Get AI prediction
                ai_prediction = self.predictor.predict_student_risk(student_data)
                
                # Update risk profile with AI insights
                if student.risk_profile and ai_prediction:
                    student.risk_profile.ml_prediction = ai_prediction.get('risk_score', 0)
                    student.risk_profile.ml_confidence = ai_prediction.get('confidence', 0)
                    student.risk_profile.risk_reasons = ', '.join(ai_prediction.get('key_factors', []))
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating AI prediction for student {student.id}: {e}")
        
        db.session.commit()
        logger.info(f"Updated AI predictions for {updated_count} students")
    
    def cleanup_old_data(self):
        """Clean up old data to maintain database performance"""
        logger.info("Cleaning up old data...")
        
        try:
            # Deactivate alerts older than 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            old_alerts = Alert.query.filter(
                Alert.created_at < thirty_days_ago,
                Alert.status == 'Active'
            ).all()
            
            for alert in old_alerts:
                alert.status = 'Resolved'
            
            # Archive old mood logs (keep last 90 days)
            ninety_days_ago = date.today() - timedelta(days=90)
            from models_support import MoodLog
            
            old_mood_logs = MoodLog.query.filter(
                MoodLog.log_date < ninety_days_ago
            ).all()
            
            # In a real system, you might move these to an archive table
            # For now, we'll just delete very old records
            deleted_count = len(old_mood_logs)
            for mood_log in old_mood_logs:
                db.session.delete(mood_log)
            
            db.session.commit()
            logger.info(f"Deactivated {len(old_alerts)} old alerts, deleted {deleted_count} old mood logs")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def start_scheduler(self):
        """Start the scheduled task runner"""
        logger.info("Starting auto data updater scheduler...")
        
        # Schedule daily updates at 2:00 AM
        schedule.every().day.at("02:00").do(self.run_daily_updates)
        
        # Schedule hourly risk updates during business hours (8 AM - 8 PM)
        for hour in range(8, 21):  # 8 AM to 8 PM
            schedule.every().day.at(f"{hour:02d}:00").do(self.update_risk_assessments)
        
        logger.info("Scheduler started. Daily updates scheduled for 2:00 AM")
        
        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function to run the auto updater"""
    updater = AutoDataUpdater()
    
    # Run updates immediately on start (optional)
    # updater.run_daily_updates()
    
    # Start the scheduler
    updater.start_scheduler()

if __name__ == '__main__':
    main()
