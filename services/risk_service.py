from models_new import db, Student, Attendance, AcademicRecord, RiskProfile, RiskLevel, AttendanceStatus
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class RiskCalculationError(Exception):
    """Custom risk calculation error"""
    pass

class DropoutRiskService:
    """Service for calculating and managing student dropout risk"""
    
    # Risk calculation weights (configurable)
    ATTENDANCE_WEIGHT = 0.6
    ACADEMIC_WEIGHT = 0.4
    
    # Risk thresholds
    HIGH_RISK_THRESHOLD = 70.0
    MEDIUM_RISK_THRESHOLD = 40.0
    
    # Critical thresholds
    CRITICAL_ATTENDANCE_THRESHOLD = 60.0
    CRITICAL_ACADEMIC_THRESHOLD = 50.0
    
    @classmethod
    def calculate_student_risk(cls, student_id: int) -> RiskProfile:
        """
        Calculate comprehensive risk score for a student
        
        Args:
            student_id: ID of the student
            
        Returns:
            RiskProfile: Updated risk profile
            
        Raises:
            RiskCalculationError: If calculation fails
        """
        try:
            student = Student.query.get(student_id)
            if not student:
                raise RiskCalculationError(f"Student not found: {student_id}")
            
            # Calculate individual risk factors
            attendance_data = cls._calculate_attendance_risk(student)
            academic_data = cls._calculate_academic_risk(student)
            behavioral_data = cls._calculate_behavioral_risk(student)
            
            # Calculate weighted risk score
            risk_score = cls._calculate_weighted_risk_score(
                attendance_data['risk_factor'],
                academic_data['risk_factor'],
                behavioral_data['risk_factor']
            )
            
            # Determine risk level
            risk_level = cls._determine_risk_level(risk_score, attendance_data, academic_data)
            
            # Apply critical overrides
            risk_score, risk_level = cls._apply_critical_overrides(
                risk_score, risk_level, attendance_data, academic_data
            )
            
            # Update or create risk profile
            risk_profile = cls._update_risk_profile(
                student, risk_score, risk_level, 
                attendance_data, academic_data, behavioral_data
            )
            
            logger.info(f"Risk calculated for student {student.full_name}: {risk_level.value} ({risk_score:.2f})")
            return risk_profile
            
        except Exception as e:
            logger.error(f"Risk calculation error for student {student_id}: {str(e)}")
            raise RiskCalculationError(f"Failed to calculate risk: {str(e)}")
    
    @classmethod
    def _calculate_attendance_risk(cls, student: Student) -> Dict:
        """Calculate attendance-based risk factor"""
        try:
            # Get attendance data for last 30 days
            cutoff_date = datetime.utcnow().date() - timedelta(days=30)
            attendance_records = student.attendance_records.filter(
                Attendance.date >= cutoff_date
            ).all()
            
            if not attendance_records:
                return {
                    'rate': 100.0,
                    'risk_factor': 0.0,
                    'trend': 'stable',
                    'total_days': 0,
                    'present_days': 0,
                    'absent_days': 0,
                    'late_days': 0
                }
            
            # Calculate attendance statistics
            total_days = len(attendance_records)
            present_days = len([r for r in attendance_records if r.status == AttendanceStatus.PRESENT])
            late_days = len([r for r in attendance_records if r.status == AttendanceStatus.LATE])
            absent_days = len([r for r in attendance_records if r.status == AttendanceStatus.ABSENT])
            
            # Calculate effective attendance rate (Late counts as half present)
            effective_present = present_days + (late_days * 0.5)
            attendance_rate = (effective_present / total_days) * 100.0
            
            # Calculate risk factor (inverse of attendance)
            risk_factor = max(0, 100 - attendance_rate)
            
            # Determine trend
            trend = cls._calculate_attendance_trend(attendance_records)
            
            return {
                'rate': round(attendance_rate, 2),
                'risk_factor': round(risk_factor, 2),
                'trend': trend,
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'late_days': late_days
            }
            
        except Exception as e:
            logger.error(f"Attendance risk calculation error: {str(e)}")
            return {
                'rate': 100.0,
                'risk_factor': 0.0,
                'trend': 'unknown',
                'total_days': 0,
                'present_days': 0,
                'absent_days': 0,
                'late_days': 0
            }
    
    @classmethod
    def _calculate_academic_risk(cls, student: Student) -> Dict:
        """Calculate academic performance-based risk factor"""
        try:
            # Get academic records for current semester
            current_semester = student.semester
            academic_records = student.academic_records.filter_by(
                semester=current_semester
            ).all()
            
            if not academic_records:
                return {
                    'average_score': 100.0,
                    'risk_factor': 0.0,
                    'trend': 'stable',
                    'total_subjects': 0,
                    'passing_subjects': 0,
                    'failing_subjects': 0
                }
            
            # Calculate academic statistics
            total_percentage = 0
            passing_subjects = 0
            failing_subjects = 0
            
            for record in academic_records:
                percentage = record.percentage
                total_percentage += percentage
                
                if percentage >= 40.0:  # Passing threshold
                    passing_subjects += 1
                else:
                    failing_subjects += 1
            
            average_score = total_percentage / len(academic_records)
            risk_factor = max(0, 100 - average_score)
            
            # Determine trend
            trend = cls._calculate_academic_trend(academic_records)
            
            return {
                'average_score': round(average_score, 2),
                'risk_factor': round(risk_factor, 2),
                'trend': trend,
                'total_subjects': len(academic_records),
                'passing_subjects': passing_subjects,
                'failing_subjects': failing_subjects
            }
            
        except Exception as e:
            logger.error(f"Academic risk calculation error: {str(e)}")
            return {
                'average_score': 100.0,
                'risk_factor': 0.0,
                'trend': 'unknown',
                'total_subjects': 0,
                'passing_subjects': 0,
                'failing_subjects': 0
            }
    
    @classmethod
    def _calculate_behavioral_risk(cls, student: Student) -> Dict:
        """Calculate behavioral risk factor based on interventions"""
        try:
            # Get intervention history
            interventions = student.interventions.order_by(
                Intervention.date.desc()
            ).limit(10).all()
            
            if not interventions:
                return {
                    'risk_factor': 0.0,
                    'total_interventions': 0,
                    'open_interventions': 0,
                    'severity_score': 0.0
                }
            
            # Calculate behavioral metrics
            total_interventions = len(interventions)
            open_interventions = len([i for i in interventions if i.status.value == 'Open'])
            
            # Calculate severity score based on intervention types
            severity_score = 0.0
            for intervention in interventions:
                if intervention.type.value == 'Counseling':
                    severity_score += 2.0
                elif intervention.type.value == 'Parent Meeting':
                    severity_score += 3.0
                elif intervention.type.value == 'Remedial Class':
                    severity_score += 1.5
                else:
                    severity_score += 1.0
            
            # Normalize severity score
            max_possible_severity = total_interventions * 3.0
            if max_possible_severity > 0:
                severity_score = (severity_score / max_possible_severity) * 100
            
            # Calculate risk factor (higher for more interventions)
            risk_factor = min(100, (total_interventions * 10) + (open_interventions * 15) + severity_score)
            
            return {
                'risk_factor': round(risk_factor, 2),
                'total_interventions': total_interventions,
                'open_interventions': open_interventions,
                'severity_score': round(severity_score, 2)
            }
            
        except Exception as e:
            logger.error(f"Behavioral risk calculation error: {str(e)}")
            return {
                'risk_factor': 0.0,
                'total_interventions': 0,
                'open_interventions': 0,
                'severity_score': 0.0
            }
    
    @classmethod
    def _calculate_weighted_risk_score(cls, attendance_factor: float, academic_factor: float, behavioral_factor: float) -> float:
        """Calculate weighted risk score"""
        # Use primary weights for attendance and academic, behavioral as modifier
        base_score = (attendance_factor * cls.ATTENDANCE_WEIGHT) + (academic_factor * cls.ACADEMIC_WEIGHT)
        
        # Add behavioral factor as modifier (reduced weight)
        behavioral_modifier = (behavioral_factor * 0.2)
        
        total_score = base_score + behavioral_modifier
        
        # Ensure score is within bounds
        return max(0, min(100, total_score))
    
    @classmethod
    def _determine_risk_level(cls, risk_score: float, attendance_data: Dict, academic_data: Dict) -> RiskLevel:
        """Determine risk level based on score and factors"""
        if risk_score >= cls.HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH
        elif risk_score >= cls.MEDIUM_RISK_THRESHOLD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    @classmethod
    def _apply_critical_overrides(cls, risk_score: float, risk_level: RiskLevel, 
                                attendance_data: Dict, academic_data: Dict) -> Tuple[float, RiskLevel]:
        """Apply critical threshold overrides"""
        # Critical attendance override
        if attendance_data['rate'] < cls.CRITICAL_ATTENDANCE_THRESHOLD:
            risk_score = max(risk_score, 85.0)
            risk_level = RiskLevel.HIGH
        
        # Critical academic override
        if academic_data['average_score'] < cls.CRITICAL_ACADEMIC_THRESHOLD:
            risk_score = max(risk_score, 80.0)
            risk_level = RiskLevel.HIGH
        
        return risk_score, risk_level
    
    @classmethod
    def _update_risk_profile(cls, student: Student, risk_score: float, risk_level: RiskLevel,
                           attendance_data: Dict, academic_data: Dict, behavioral_data: Dict) -> RiskProfile:
        """Update or create risk profile"""
        try:
            # Get existing profile or create new one
            risk_profile = student.risk_profile
            if not risk_profile:
                risk_profile = RiskProfile(student_id=student.id)
                db.session.add(risk_profile)
            
            # Update profile data
            risk_profile.risk_score = round(risk_score, 2)
            risk_profile.risk_level = risk_level
            risk_profile.attendance_factor = attendance_data['risk_factor']
            risk_profile.academic_factor = academic_data['risk_factor']
            risk_profile.behavioral_factor = behavioral_data['risk_factor']
            risk_profile.attendance_rate = attendance_data['rate']
            risk_profile.average_score = academic_data['average_score']
            risk_profile.last_updated = datetime.utcnow()
            
            db.session.commit()
            return risk_profile
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Risk profile update error: {str(e)}")
            raise RiskCalculationError(f"Failed to update risk profile: {str(e)}")
    
    @classmethod
    def _calculate_attendance_trend(cls, records: List) -> str:
        """Calculate attendance trend"""
        if len(records) < 7:
            return 'insufficient_data'
        
        # Split records into two halves
        mid_point = len(records) // 2
        first_half = records[:mid_point]
        second_half = records[mid_point:]
        
        # Calculate attendance rates for each half
        def calculate_rate(recs):
            if not recs:
                return 0
            present = len([r for r in recs if r.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE]])
            return (present / len(recs)) * 100
        
        first_rate = calculate_rate(first_half)
        second_rate = calculate_rate(second_half)
        
        # Determine trend
        if second_rate > first_rate + 5:
            return 'improving'
        elif second_rate < first_rate - 5:
            return 'declining'
        else:
            return 'stable'
    
    @classmethod
    def _calculate_academic_trend(cls, records: List) -> str:
        """Calculate academic performance trend"""
        if len(records) < 3:
            return 'insufficient_data'
        
        # Sort by date
        sorted_records = sorted(records, key=lambda x: x.date)
        
        # Compare recent vs older performance
        recent_records = sorted_records[-3:]  # Last 3 records
        older_records = sorted_records[:-3]   # Earlier records
        
        if not older_records:
            return 'insufficient_data'
        
        recent_avg = sum(r.percentage for r in recent_records) / len(recent_records)
        older_avg = sum(r.percentage for r in older_records) / len(older_records)
        
        # Determine trend
        if recent_avg > older_avg + 5:
            return 'improving'
        elif recent_avg < older_avg - 5:
            return 'declining'
        else:
            return 'stable'
    
    @classmethod
    def batch_update_risk_scores(cls, student_ids: List[int] = None) -> Dict:
        """
        Update risk scores for multiple students
        
        Args:
            student_ids: List of student IDs (None for all students)
            
        Returns:
            Dict: Update statistics
        """
        try:
            if student_ids is None:
                students = Student.query.all()
            else:
                students = Student.query.filter(Student.id.in_(student_ids)).all()
            
            updated_count = 0
            failed_count = 0
            errors = []
            
            for student in students:
                try:
                    cls.calculate_student_risk(student.id)
                    updated_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Student {student.id}: {str(e)}")
            
            result = {
                'total_students': len(students),
                'updated_count': updated_count,
                'failed_count': failed_count,
                'errors': errors
            }
            
            logger.info(f"Batch risk update completed: {updated_count}/{len(students)} successful")
            return result
            
        except Exception as e:
            logger.error(f"Batch risk update error: {str(e)}")
            raise RiskCalculationError(f"Batch update failed: {str(e)}")
    
    @classmethod
    def get_risk_statistics(cls) -> Dict:
        """Get overall risk statistics"""
        try:
            total_students = Student.query.count()
            
            if total_students == 0:
                return {
                    'total_students': 0,
                    'risk_distribution': {'Low': 0, 'Medium': 0, 'High': 0},
                    'average_risk_score': 0.0,
                    'high_risk_percentage': 0.0
                }
            
            # Get risk distribution
            risk_profiles = RiskProfile.query.all()
            risk_distribution = {'Low': 0, 'Medium': 0, 'High': 0}
            total_risk_score = 0
            
            for profile in risk_profiles:
                risk_distribution[profile.risk_level.value] += 1
                total_risk_score += profile.risk_score
            
            average_risk_score = total_risk_score / len(risk_profiles) if risk_profiles else 0
            high_risk_percentage = (risk_distribution['High'] / total_students) * 100
            
            return {
                'total_students': total_students,
                'risk_distribution': risk_distribution,
                'average_risk_score': round(average_risk_score, 2),
                'high_risk_percentage': round(high_risk_percentage, 2)
            }
            
        except Exception as e:
            logger.error(f"Risk statistics error: {str(e)}")
            return {
                'total_students': 0,
                'risk_distribution': {'Low': 0, 'Medium': 0, 'High': 0},
                'average_risk_score': 0.0,
                'high_risk_percentage': 0.0
            }
