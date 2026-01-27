from flask import current_app
from flask_mail import Message
from threading import Thread
from datetime import datetime, timedelta

def send_async_email(app, msg):
    with app.app_context():
        try:
            from flask_mail import mail
            mail.send(msg)
            current_app.logger.info(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")

def send_email(subject, recipients, html_body, text_body=None):
    """
    Send an email asynchronously
    """
    if not current_app.config.get('MAIL_USERNAME'):
        current_app.logger.warning("Email not configured. Skipping email send.")
        return False
        
    from flask_mail import Message
    msg = Message(
        subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=recipients
    )
    
    msg.html = html_body
    if text_body:
        msg.body = text_body
    
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    return True

def send_risk_alert_email(student, risk_profile):
    """
    Send email alert when student risk level changes to High
    """
    subject = f"🚨 High Risk Alert: {student.full_name()}"
    
    html_body = f"""
    <html>
    <body>
        <h2>Student Risk Alert - EduGuard System</h2>
        <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #721c24;">⚠️ High Risk Student Identified</h3>
        </div>
        
        <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Student Name:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{student.full_name()}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Student ID:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{student.student_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Email:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{student.email}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Risk Score:</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #dc3545; font-weight: bold;">{risk_profile.risk_score}/100</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Risk Level:</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #dc3545; font-weight: bold;">{risk_profile.risk_level}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Attendance Factor:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{risk_profile.attendance_factor}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Academic Factor:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{risk_profile.academic_factor}</td>
            </tr>
        </table>
        
        <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4>Recommended Actions:</h4>
            <ul>
                <li>Schedule an immediate counseling session</li>
                <li>Contact parents/guardians</li>
                <li>Review recent attendance patterns</li>
                <li>Assess academic support needs</li>
                <li>Document intervention plan</li>
            </ul>
        </div>
        
        <p><strong>Please log into the EduGuard system to take appropriate action.</strong></p>
        <p><em>This is an automated message from the EduGuard Student Dropout Prevention System.</em></p>
    </body>
    </html>
    """
    
    # Send to all faculty and admin users
    from models import User
    faculty_users = User.query.filter(User.role.in_(['faculty', 'admin'])).all()
    recipients = [user.email for user in faculty_users if user.email]
    
    if recipients:
        return send_email(subject, recipients, html_body)
    return False

def send_intervention_notification(student, intervention):
    """
    Send notification when new intervention is recorded
    """
    subject = f"Intervention Recorded: {student.full_name()}"
    
    html_body = f"""
    <html>
    <body>
        <h2>Intervention Notification - EduGuard System</h2>
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #155724;">✅ New Intervention Recorded</h3>
        </div>
        
        <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Student Name:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{student.full_name()}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Student ID:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{student.student_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Intervention Type:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{intervention.type}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Date:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{intervention.date.strftime('%Y-%m-%d')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Status:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{intervention.status}</td>
            </tr>
        </table>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4>Notes:</h4>
            <p>{intervention.notes}</p>
        </div>
        
        <p><strong>Please follow up on this intervention as needed.</strong></p>
        <p><em>This is an automated message from the EduGuard Student Dropout Prevention System.</em></p>
    </body>
    </html>
    """
    
    from models import User
    faculty_users = User.query.filter(User.role.in_(['faculty', 'admin'])).all()
    recipients = [user.email for user in faculty_users if user.email]
    
    if recipients:
        return send_email(subject, recipients, html_body)
    return False

def send_weekly_digest():
    """
    Send weekly digest of student risk statistics
    """
    from models import Student, RiskProfile
    
    subject = f"Weekly Risk Digest - EduGuard System ({datetime.now().strftime('%Y-%m-%d')})"
    
    # Get statistics
    total_students = Student.query.count()
    high_risk_count = RiskProfile.query.filter_by(risk_level='High').count()
    medium_risk_count = RiskProfile.query.filter_by(risk_level='Medium').count()
    low_risk_count = RiskProfile.query.filter_by(risk_level='Low').count()
    
    # Get high risk students
    high_risk_students = db.session.query(Student, RiskProfile).join(RiskProfile).filter(
        RiskProfile.risk_level == 'High'
    ).order_by(RiskProfile.risk_score.desc()).limit(10).all()
    
    html_body = f"""
    <html>
    <body>
        <h2>Weekly Student Risk Digest - EduGuard System</h2>
        <p>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3>📊 Risk Distribution Overview</h3>
            <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Total Students:</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{total_students}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; color: #dc3545;">High Risk:</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: #dc3545; font-weight: bold;">{high_risk_count} ({(high_risk_count/total_students*100):.1f}%)</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; color: #ffc107;">Medium Risk:</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: #ffc107; font-weight: bold;">{medium_risk_count} ({(medium_risk_count/total_students*100):.1f}%)</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; color: #28a745;">Low Risk:</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: #28a745; font-weight: bold;">{low_risk_count} ({(low_risk_count/total_students*100):.1f}%)</td>
                </tr>
            </table>
        </div>
    """
    
    if high_risk_students:
        html_body += """
        <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #721c24;">🚨 Top High Risk Students</h3>
            <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                <tr style="background-color: #f5c6cb;">
                    <th style="padding: 8px; border: 1px solid #ddd;">Student Name</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Student ID</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Risk Score</th>
                    <th style="padding: 8px; border: 1px solid #ddd;">Email</th>
                </tr>
        """
        
        for student, risk_profile in high_risk_students:
            html_body += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{student.full_name()}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{student.student_id}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: #dc3545; font-weight: bold;">{risk_profile.risk_score}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{student.email}</td>
                </tr>
            """
        
        html_body += """
            </table>
        </div>
        """
    
    html_body += """
        <p><strong>Please review this data and take appropriate actions for at-risk students.</strong></p>
        <p><em>This is an automated weekly digest from the EduGuard Student Dropout Prevention System.</em></p>
    </body>
    </html>
    """
    
    from models import User
    faculty_users = User.query.filter(User.role.in_(['faculty', 'admin'])).all()
    recipients = [user.email for user in faculty_users if user.email]
    
    if recipients:
        return send_email(subject, recipients, html_body)
    return False
