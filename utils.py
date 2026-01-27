from datetime import datetime
from models import db, RiskProfile, Attendance, AcademicRecord

def calculate_attendance_percentage(student):
    total_days = Attendance.query.filter_by(student_id=student.id).count()
    if total_days == 0:
        return 100.0 # Default to 100 if no records
    
    present_days = Attendance.query.filter_by(student_id=student.id, status='Present').count()
    # Count 'Late' as present or half? Let's count Late as Present for simplicity but maybe flag it.
    # Or just count strictly present. Let's count Late as 1 and Excused as 0 (ignored) or 1?
    # Let's stick to simple: Present + Late = Present.
    
    late_days = Attendance.query.filter_by(student_id=student.id, status='Late').count()
    effective_present = present_days + late_days
    
    return (effective_present / total_days) * 100.0

def calculate_academic_average(student):
    records = AcademicRecord.query.filter_by(student_id=student.id).all()
    if not records:
        return 100.0 # Default to 100 if no records
    
    total_percentage = 0
    for record in records:
        if record.max_score > 0:
            total_percentage += (record.score / record.max_score) * 100.0
            
    return total_percentage / len(records)

def update_student_risk(student):
    """
    Analyzes student data and updates their RiskProfile.
    Logic:
    - Attendance Weight: 50%
    - Academic Weight: 50%
    
    Thresholds:
    - Risk Score > 70: High Risk
    - Risk Score > 40: Medium Risk
    - Else: Low Risk
    
    Inverse Logic:
    - High Attendance + High Grades = Low Risk Score
    - Low Attendance + Low Grades = High Risk Score
    """
    
    att_pct = calculate_attendance_percentage(student)
    acad_pct = calculate_academic_average(student)
    
    # Calculate Risk Factors (Inverted: Lower pct = Higher Risk)
    # 100% attendance = 0 risk from attendance
    # 0% attendance = 100 risk from attendance
    att_risk_factor = max(0, 100 - att_pct)
    acad_risk_factor = max(0, 100 - acad_pct)
    
    # Weighted Average Risk Score
    # We can adjust weights. Attendance is often the biggest predictor.
    # Let's say Attendance 60%, Academic 40%
    total_risk_score = (att_risk_factor * 0.6) + (acad_risk_factor * 0.4)
    
    # Determine Level
    if total_risk_score >= 50: # If avg is below 50% basically
        risk_level = 'High'
    elif total_risk_score >= 30: # If avg is below 70%
        risk_level = 'Medium'
    else:
        risk_level = 'Low'
        
    # Override Rules (Critical Failures)
    # If attendance < 60%, immediately High Risk regardless of grades
    if att_pct < 60:
        risk_level = 'High'
        total_risk_score = max(total_risk_score, 80) # Force high score
        
    # Update or Create Profile
    profile = RiskProfile.query.filter_by(student_id=student.id).first()
    if not profile:
        profile = RiskProfile(student_id=student.id)
    
    profile.risk_score = round(total_risk_score, 2)
    profile.risk_level = risk_level
    profile.attendance_factor = round(att_risk_factor, 2)
    profile.academic_factor = round(acad_risk_factor, 2)
    profile.last_updated = datetime.utcnow()
    
    db.session.add(profile)
    db.session.commit()
    
    return profile
