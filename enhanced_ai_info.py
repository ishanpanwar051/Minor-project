#!/usr/bin/env python3
"""
Enhanced AI Information System for Students
Provides detailed AI analysis and recommendations
"""

from models import Student, RiskProfile, Attendance, db
from enhanced_ai_predictor import EnhancedRiskPredictor
from datetime import datetime, date, timedelta
import json

class StudentAIInfo:
    """AI-powered student information and recommendation system"""
    
    def __init__(self):
        self.predictor = EnhancedRiskPredictor()
        
    def get_student_comprehensive_info(self, student_id):
        """Get comprehensive AI analysis for a specific student"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return None
                
            # Get student data
            student_data = self._prepare_student_data(student)
            
            # AI predictions
            ai_analysis = self.predictor.predict_student_risk(student_data)
            
            # Risk factors analysis
            risk_factors = self._analyze_risk_factors(student)
            
            # Recommendations
            recommendations = self._generate_recommendations(student, ai_analysis, risk_factors)
            
            # Academic trends
            academic_trends = self._analyze_academic_trends(student)
            
            # Attendance patterns
            attendance_patterns = self._analyze_attendance_patterns(student)
            
            # Support resources
            support_resources = self._get_support_resources(student)
            
            return {
                'student_info': {
                    'name': f"{student.first_name} {student.last_name}",
                    'student_id': student.student_id,
                    'department': student.department,
                    'year': student.year,
                    'semester': student.semester,
                    'gpa': student.gpa
                },
                'ai_analysis': ai_analysis,
                'risk_factors': risk_factors,
                'recommendations': recommendations,
                'academic_trends': academic_trends,
                'attendance_patterns': attendance_patterns,
                'support_resources': support_resources,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting student info: {e}")
            return None
    
    def _prepare_student_data(self, student):
        """Prepare student data for AI analysis"""
        risk_profile = student.risk_profile
        
        return {
            'gpa': student.gpa or 0,
            'attendance_rate': risk_profile.attendance_rate if risk_profile else 85,
            'academic_performance': risk_profile.academic_performance if risk_profile else 75,
            'credits_completed': student.credits_completed or 0,
            'year': student.year or 1,
            'semester': student.semester or 1,
            'financial_issues': risk_profile.financial_issues if risk_profile else False,
            'family_problems': risk_profile.family_problems if risk_profile else False,
            'health_issues': risk_profile.health_issues if risk_profile else False,
            'social_isolation': risk_profile.social_isolation if risk_profile else False,
            'mental_wellbeing_score': risk_profile.mental_wellbeing_score if risk_profile else 8
        }
    
    def _analyze_risk_factors(self, student):
        """Analyze specific risk factors for the student"""
        risk_profile = student.risk_profile
        if not risk_profile:
            return []
            
        factors = []
        
        # Academic factors
        if student.gpa and student.gpa < 6.0:
            factors.append({
                'category': 'Academic',
                'factor': 'Low GPA',
                'severity': 'High' if student.gpa < 5.0 else 'Medium',
                'description': f'GPA of {student.gpa} is below acceptable level',
                'recommendation': 'Focus on improving study habits and seek academic support'
            })
        
        # Attendance factors
        if risk_profile.attendance_rate and risk_profile.attendance_rate < 75:
            factors.append({
                'category': 'Attendance',
                'factor': 'Poor Attendance',
                'severity': 'High' if risk_profile.attendance_rate < 60 else 'Medium',
                'description': f'Attendance rate of {risk_profile.attendance_rate}% is concerning',
                'recommendation': 'Attend classes regularly and communicate with faculty about any issues'
            })
        
        # Personal factors
        if risk_profile.financial_issues:
            factors.append({
                'category': 'Personal',
                'factor': 'Financial Issues',
                'severity': 'High',
                'description': 'Student is facing financial difficulties',
                'recommendation': 'Explore scholarship options and financial aid resources'
            })
        
        if risk_profile.family_problems:
            factors.append({
                'category': 'Personal',
                'factor': 'Family Problems',
                'severity': 'High',
                'description': 'Student is experiencing family-related issues',
                'recommendation': 'Seek counseling support and maintain open communication'
            })
        
        if risk_profile.health_issues:
            factors.append({
                'category': 'Personal',
                'factor': 'Health Issues',
                'severity': 'Medium',
                'description': 'Student has health-related concerns',
                'recommendation': 'Utilize campus health services and maintain wellness routine'
            })
        
        if risk_profile.social_isolation:
            factors.append({
                'category': 'Social',
                'factor': 'Social Isolation',
                'severity': 'Medium',
                'description': 'Student shows signs of social isolation',
                'recommendation': 'Participate in campus activities and join student organizations'
            })
        
        # Mental wellbeing
        if risk_profile.mental_wellbeing_score and risk_profile.mental_wellbeing_score < 6:
            factors.append({
                'category': 'Mental Health',
                'factor': 'Low Mental Wellbeing',
                'severity': 'High' if risk_profile.mental_wellbeing_score < 4 else 'Medium',
                'description': f'Mental wellbeing score of {risk_profile.mental_wellbeing_score} needs attention',
                'recommendation': 'Seek counseling services and practice stress management techniques'
            })
        
        return factors
    
    def _generate_recommendations(self, student, ai_analysis, risk_factors):
        """Generate personalized recommendations based on AI analysis"""
        recommendations = []
        risk_level = ai_analysis.get('risk_level', 'Low')
        
        # Academic recommendations
        if student.gpa and student.gpa < 7.0:
            recommendations.extend([
                {
                    'category': 'Academic',
                    'priority': 'High',
                    'title': 'Improve Academic Performance',
                    'description': 'Focus on improving your GPA through better study habits',
                    'actions': [
                        'Create a structured study schedule',
                        'Join study groups with classmates',
                        'Seek help from professors during office hours',
                        'Utilize campus tutoring services'
                    ]
                }
            ])
        
        # Attendance recommendations
        risk_profile = student.risk_profile
        if risk_profile and risk_profile.attendance_rate and risk_profile.attendance_rate < 80:
            recommendations.append({
                'category': 'Attendance',
                'priority': 'High',
                'title': 'Improve Class Attendance',
                'description': 'Regular attendance is crucial for academic success',
                'actions': [
                    'Set daily alarms for classes',
                    'Prepare materials the night before',
                    'Find a study buddy to keep you accountable',
                    'Contact faculty if you need to miss class'
                ]
            })
        
        # Risk-specific recommendations
        if risk_level in ['High', 'Critical']:
            recommendations.append({
                'category': 'Urgent',
                'priority': 'Critical',
                'title': 'Immediate Support Required',
                'description': 'Your risk level requires immediate attention',
                'actions': [
                    'Schedule an appointment with a counselor',
                    'Speak with your academic advisor',
                    'Contact student support services',
                    'Inform your parents/guardians about your situation'
                ]
            })
        
        # General wellness recommendations
        recommendations.append({
            'category': 'Wellness',
            'priority': 'Medium',
            'title': 'Maintain Well-being',
            'description': 'Take care of your physical and mental health',
            'actions': [
                'Get 7-8 hours of sleep each night',
                'Exercise regularly (30 minutes daily)',
                'Practice stress management techniques',
                'Maintain a balanced diet'
            ]
        })
        
        return recommendations
    
    def _analyze_academic_trends(self, student):
        """Analyze academic performance trends"""
        # This would typically analyze historical data
        # For now, return current status with trend indicators
        return {
            'current_gpa': student.gpa or 0,
            'trend': 'Stable',  # Would be calculated from historical data
            'credits_completed': student.credits_completed or 0,
            'credits_needed': (4 - (student.year or 1)) * 30,  # Estimate
            'performance_prediction': 'Good' if (student.gpa or 0) >= 7.0 else 'Needs Improvement'
        }
    
    def _analyze_attendance_patterns(self, student):
        """Analyze attendance patterns and trends"""
        risk_profile = student.risk_profile
        if not risk_profile:
            return {
                'overall_rate': 85,
                'trend': 'Stable',
                'concerns': []
            }
        
        concerns = []
        if risk_profile.attendance_rate < 75:
            concerns.append('Attendance below recommended level')
        
        return {
            'overall_rate': risk_profile.attendance_rate or 85,
            'trend': 'Declining' if risk_profile.attendance_rate < 70 else 'Stable',
            'concerns': concerns
        }
    
    def _get_support_resources(self, student):
        """Get relevant support resources for the student"""
        resources = [
            {
                'name': 'Academic Counseling',
                'description': 'Get help with course selection and academic planning',
                'contact': 'counseling@eduguard.edu',
                'location': 'Student Services Building, Room 101'
            },
            {
                'name': 'Mental Health Services',
                'description': 'Professional counseling and mental health support',
                'contact': 'mentalhealth@eduguard.edu',
                'location': 'Health Center, Room 205'
            },
            {
                'name': 'Financial Aid Office',
                'description': 'Scholarships, grants, and financial assistance',
                'contact': 'finaid@eduguard.edu',
                'location': 'Admin Building, Room 301'
            },
            {
                'name': 'Career Services',
                'description': 'Career planning and job placement assistance',
                'contact': 'careers@eduguard.edu',
                'location': 'Career Center, Room 150'
            }
        ]
        
        # Add specific resources based on student's risk factors
        risk_profile = student.risk_profile
        if risk_profile:
            if risk_profile.financial_issues:
                resources.append({
                    'name': 'Emergency Financial Assistance',
                    'description': 'Short-term financial help for students in crisis',
                    'contact': 'emergency@eduguard.edu',
                    'location': 'Student Services Building, Room 102'
                })
            
            if risk_profile.health_issues or (risk_profile.mental_wellbeing_score and risk_profile.mental_wellbeing_score < 6):
                resources.append({
                    'name': '24/7 Crisis Hotline',
                    'description': 'Immediate support for mental health crises',
                    'contact': '1-800-HELP-NOW',
                    'location': 'Available 24/7 by phone'
                })
        
        return resources

# Global instance
student_ai_info = StudentAIInfo()
