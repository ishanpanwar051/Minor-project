"""
Alert Service for Early Warning System
Handles automated email and SMS alerts based on risk levels
"""

from flask import current_app
from datetime import datetime, timedelta
from models import db, User, Student, RiskProfile
from email_service import send_email
import requests
import json

class AlertService:
    """Service for managing early warning alerts"""
    
    @staticmethod
    def check_and_send_alerts(student, new_risk_score, previous_risk_score=None):
        """
        Check risk levels and send appropriate alerts
        Risk Levels: Low (<40%), Medium (40-70%), High (70-85%), Critical (>85%)
        """
        try:
            # Determine risk level
            risk_level = AlertService._calculate_risk_level(new_risk_score)
            
            # Send alerts based on risk level
            if new_risk_score > 85:  # Critical Risk
                AlertService._send_critical_alert(student, new_risk_score, risk_level)
                AlertService._send_sms_alert(student, new_risk_score, risk_level)
            elif new_risk_score > 70:  # High Risk
                AlertService._send_high_risk_alert(student, new_risk_score, risk_level)
            elif new_risk_score > 40:  # Medium Risk
                AlertService._send_medium_risk_alert(student, new_risk_score, risk_level)
            
            # Log the alert
            AlertService._log_alert(student, new_risk_score, risk_level)
            
            current_app.logger.info(f"Alert processed for {student.full_name()}: Risk {new_risk_score}% ({risk_level})")
            
        except Exception as e:
            current_app.logger.error(f"Error in alert service: {str(e)}")
    
    @staticmethod
    def _calculate_risk_level(risk_score):
        """Calculate risk level based on percentage"""
        if risk_score > 85:
            return 'Critical'
        elif risk_score > 70:
            return 'High'
        elif risk_score > 40:
            return 'Medium'
        else:
            return 'Low'
    
    @staticmethod
    def _send_critical_alert(student, risk_score, risk_level):
        """Send critical risk alert (email + SMS)"""
        subject = f"🚨 CRITICAL ALERT: {student.full_name()} - Immediate Action Required"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">🚨 CRITICAL RISK ALERT</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Immediate Intervention Required</p>
                </div>
                
                <div style="padding: 30px;">
                    <h2 style="color: #dc3545; margin-bottom: 20px;">Student Information</h2>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Name:</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{student.full_name()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Student ID:</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{student.student_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Department:</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{student.department or 'N/A'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Risk Score:</td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: #dc3545; font-weight: bold; font-size: 18px;">{risk_score}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Risk Level:</td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: #dc3545; font-weight: bold; font-size: 16px;">{risk_level}</td>
                        </tr>
                    </table>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 15px; margin-bottom: 20px;">
                        <h3 style="color: #856404; margin-top: 0;">⚠️ IMMEDIATE ACTIONS REQUIRED:</h3>
                        <ol style="color: #856404;">
                            <li><strong>Emergency counseling session within 24 hours</strong></li>
                            <li><strong>Contact parents/guardians immediately</strong></li>
                            <li><strong>Academic probation review</strong></li>
                            <li><strong>Document intervention plan</strong></li>
                            <li><strong>Daily monitoring required</strong></li>
                        </ol>
                    </div>
                    
                    <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 4px; padding: 15px;">
                        <h3 style="color: #0c5460; margin-top: 0;">📞 Contact Information</h3>
                        <p><strong>Student Email:</strong> {student.email or 'N/A'}</p>
                        <p><strong>Student Phone:</strong> {student.phone or 'N/A'}</p>
                    </div>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 8px 8px;">
                    <p style="margin: 0; color: #6c757d;">
                        <strong>This is a CRITICAL priority alert from the EduGuard Student Dropout Prevention System.</strong><br>
                        Please take immediate action to support this student.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send to all faculty and admin
        recipients = AlertService._get_faculty_recipients()
        if recipients:
            send_email(subject, recipients, html_body)
    
    @staticmethod
    def _send_high_risk_alert(student, risk_score, risk_level):
        """Send high risk alert (email only)"""
        subject = f"⚠️ High Risk Alert: {student.full_name()}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <div style="background-color: #ffc107; color: #000; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">⚠️ HIGH RISK ALERT</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Student Requires Attention</p>
                </div>
                
                <div style="padding: 30px;">
                    <h2 style="color: #856404; margin-bottom: 20px;">Student Information</h2>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Name:</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{student.full_name()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Student ID:</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{student.student_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Risk Score:</td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: #856404; font-weight: bold;">{risk_score}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Risk Level:</td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: #856404; font-weight: bold;">{risk_level}</td>
                        </tr>
                    </table>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 15px; margin-bottom: 20px;">
                        <h3 style="color: #856404; margin-top: 0;">📋 Recommended Actions:</h3>
                        <ul style="color: #856404;">
                            <li>Schedule counseling session within 48 hours</li>
                            <li>Review academic performance</li>
                            <li>Assess attendance patterns</li>
                            <li>Consider academic support services</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        recipients = AlertService._get_faculty_recipients()
        if recipients:
            send_email(subject, recipients, html_body)
    
    @staticmethod
    def _send_medium_risk_alert(student, risk_score, risk_level):
        """Send medium risk alert (email notification)"""
        subject = f"📊 Risk Update: {student.full_name()} - {risk_level} Risk"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <div style="background-color: #17a2b8; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">📊 Risk Level Update</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Student Risk Assessment</p>
                </div>
                
                <div style="padding: 30px;">
                    <h2 style="color: #17a2b8; margin-bottom: 20px;">Student Information</h2>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Name:</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{student.full_name()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Student ID:</td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{student.student_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Risk Score:</td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: #17a2b8; font-weight: bold;">{risk_score}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f8f9fa;">Risk Level:</td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: #17a2b8; font-weight: bold;">{risk_level}</td>
                        </tr>
                    </table>
                    
                    <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 4px; padding: 15px;">
                        <h3 style="color: #0c5460; margin-top: 0;">💡 Recommendations:</h3>
                        <ul style="color: #0c5460;">
                            <li>Monitor student progress</li>
                            <li>Offer academic support if needed</li>
                            <li>Check attendance regularly</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        recipients = AlertService._get_faculty_recipients()
        if recipients:
            send_email(subject, recipients, html_body)
    
    @staticmethod
    def _send_sms_alert(student, risk_score, risk_level):
        """Send SMS alert for critical risk (placeholder - would integrate with SMS service)"""
        try:
            # This would integrate with an SMS service like Twilio, AWS SNS, etc.
            # For now, we'll log it
            sms_message = f"CRITICAL: {student.full_name()} ({student.student_id}) - Risk: {risk_score}% ({risk_level}). Immediate action required. EduGuard System."
            
            current_app.logger.info(f"SMS Alert would be sent: {sms_message}")
            
            # Example SMS integration (commented out):
            # from twilio.rest import Client
            # client = Client(current_app.config['TWILIO_ACCOUNT_SID'], current_app.config['TWILIO_AUTH_TOKEN'])
            # message = client.messages.create(
            #     body=sms_message,
            #     from_=current_app.config['TWILIO_PHONE_NUMBER'],
            #     to=student.phone
            # )
            
        except Exception as e:
            current_app.logger.error(f"Error sending SMS: {str(e)}")
    
    @staticmethod
    def _get_faculty_recipients():
        """Get list of faculty and admin email recipients"""
        faculty_users = User.query.filter(User.role.in_(['faculty', 'admin'])).all()
        return [user.email for user in faculty_users if user.email]
    
    @staticmethod
    def _log_alert(student, risk_score, risk_level):
        """Log alert to database"""
        try:
            from models import Alert
            alert = Alert(
                student_id=student.id,
                alert_type='Risk Level Change',
                severity=risk_level,
                title=f'{risk_level} Risk Alert',
                description=f'Student risk level changed to {risk_level} with score {risk_score}%',
                status='Active',
                created_at=datetime.utcnow()
            )
            db.session.add(alert)
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Error logging alert: {str(e)}")
    
    @staticmethod
    def check_all_students_risk():
        """Check risk levels for all students and send alerts"""
        try:
            students = Student.query.all()
            
            for student in students:
                # Get current risk profile
                risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
                
                if risk_profile and risk_profile.risk_score:
                    AlertService.check_and_send_alerts(
                        student, 
                        risk_profile.risk_score
                    )
            
            current_app.logger.info("Risk alert check completed for all students")
            
        except Exception as e:
            current_app.logger.error(f"Error in risk check: {str(e)}")
