from datetime import datetime
from models import db, RiskProfile, Attendance, AcademicRecord
import logging

logger = logging.getLogger(__name__)

def calculate_attendance_percentage(student):
    try:
        total_days = Attendance.query.filter_by(student_id=student.id).count()
        if total_days == 0:
            return 100.0  # Default to 100 if no records
        
        present_days = Attendance.query.filter_by(student_id=student.id, status='Present').count()
        late_days = Attendance.query.filter_by(student_id=student.id, status='Late').count()
        effective_present = present_days + late_days
        
        return (effective_present / total_days) * 100.0
    except Exception as e:
        logger.error(f"Error calculating attendance for student {student.id}: {str(e)}")
        return 100.0

def calculate_academic_average(student):
    try:
        records = AcademicRecord.query.filter_by(student_id=student.id).all()
        if not records:
            return 100.0  # Default to 100 if no records
        
        total_percentage = 0
        for record in records:
            if record.max_score > 0:
                total_percentage += (record.score / record.max_score) * 100.0
                
        return total_percentage / len(records)
    except Exception as e:
        logger.error(f"Error calculating academic average for student {student.id}: {str(e)}")
        return 100.0

def update_student_risk(student):
    """
    Analyzes student data and updates their RiskProfile.
    Logic:
    - Attendance Weight: 60%
    - Academic Weight: 40%
    
    Thresholds:
    - Risk Score > 50: High Risk
    - Risk Score > 30: Medium Risk
    - Else: Low Risk
    
    Inverse Logic:
    - High Attendance + High Grades = Low Risk Score
    - Low Attendance + Low Grades = High Risk Score
    """
    
    try:
        att_pct = calculate_attendance_percentage(student)
        acad_pct = calculate_academic_average(student)
        
        # Calculate Risk Factors (Inverted: Lower pct = Higher Risk)
        att_risk_factor = max(0, 100 - att_pct)
        acad_risk_factor = max(0, 100 - acad_pct)
        
        # Weighted Average Risk Score (Attendance 60%, Academic 40%)
        total_risk_score = (att_risk_factor * 0.6) + (acad_risk_factor * 0.4)
        
        # Determine Level
        if total_risk_score >= 50:
            risk_level = 'High'
        elif total_risk_score >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
            
        # Override Rules (Critical Failures)
        if att_pct < 60:
            risk_level = 'High'
            total_risk_score = max(total_risk_score, 80)
            
        # Get existing profile or create new one
        profile = RiskProfile.query.filter_by(student_id=student.id).first()
        old_risk_level = profile.risk_level if profile else None
        
        if not profile:
            profile = RiskProfile(student_id=student.id)
        
        profile.risk_score = round(total_risk_score, 2)
        profile.risk_level = risk_level
        profile.attendance_factor = round(att_risk_factor, 2)
        profile.academic_factor = round(acad_risk_factor, 2)
        profile.last_updated = datetime.utcnow()
        
        db.session.add(profile)
        db.session.commit()
        
        # Send email alert if risk level changed to High (only if email is configured)
        if old_risk_level != 'High' and risk_level == 'High':
            try:
                from flask import current_app
                if current_app.config.get('MAIL_USERNAME'):
                    from email_service import send_risk_alert_email
                    send_risk_alert_email(student, profile)
                    logger.info(f"Risk alert sent for student {student.full_name()} (ID: {student.student_id})")
            except Exception as e:
                logger.error(f"Failed to send risk alert for student {student.id}: {str(e)}")
        
        logger.info(f"Risk updated for student {student.full_name()}: {risk_level} ({total_risk_score:.2f})")
        return profile
        
    except Exception as e:
        logger.error(f"Error updating risk for student {student.id}: {str(e)}")
        # Return a default profile
        profile = RiskProfile.query.filter_by(student_id=student.id).first()
        if not profile:
            profile = RiskProfile(student_id=student.id, risk_score=0.0, risk_level='Low')
            db.session.add(profile)
            db.session.commit()
        return profile

def batch_update_risk_scores():
    """
    Update risk scores for all students. This should be run as a background job.
    """
    try:
        from models import Student
        students = Student.query.all()
        updated_count = 0
        
        for student in students:
            update_student_risk(student)
            updated_count += 1
            
        logger.info(f"Batch update completed: {updated_count} students processed")
        return updated_count
    except Exception as e:
        logger.error(f"Error in batch risk update: {str(e)}")
        return 0
