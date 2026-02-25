from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
import json
import datetime
import random

# Create AI blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

# Mock AI responses (in real implementation, use OpenAI API)
AI_RESPONSES = {
    "study_help": [
        "I understand you're struggling. Let's break this down step by step. What specific subject or topic is challenging you?",
        "Many students face this challenge. Here are some effective study techniques: 1) Break problems into smaller parts, 2) Practice regularly, 3) Don't hesitate to ask for help.",
        "Let me help you create a personalized study plan for this subject. First, tell me what you're finding most difficult.",
        "I've helped many students with similar issues. The key is to identify your learning style and adapt your study methods accordingly."
    ],
    "motivation": [
        "Don't give up! Every successful person faced challenges like this. You're capable of overcoming this with the right approach.",
        "You're stronger than you think. Remember why you started this journey and how far you've already come.",
        "I believe in your ability to succeed. Let's work together to find a solution that works for you.",
        "This feeling is temporary, but your education is permanent. Let's focus on small, achievable goals to build momentum."
    ],
    "time_management": [
        "Let's create a realistic study schedule that works for you. How many hours can you dedicate to studying each day?",
        "Time management is a skill we can improve together. Try the Pomodoro technique: 25 minutes of focused study, then 5-minute breaks.",
        "I'll help you balance your studies with other responsibilities. What's taking up most of your time right now?",
        "Effective time management starts with prioritization. Let's identify your most important tasks and create a schedule."
    ],
    "career_guidance": [
        "Based on your interests, here are some career paths to consider: Tech, Healthcare, Business, Creative fields. What interests you most?",
        "Let's explore how your current studies align with your career goals. What field are you most passionate about?",
        "I can help you research different career options. What subjects do you enjoy most in your current program?",
        "Career planning is a journey. Let's start by identifying your strengths and interests, then explore matching career paths."
    ],
    "stress_help": [
        "Feeling overwhelmed is normal. Let's talk through what's causing you stress and find manageable solutions.",
        "I'm here to support you through stressful times. Remember to take breaks, practice self-care, and reach out for help when needed.",
        "Stress management is crucial for academic success. Try deep breathing exercises, regular exercise, and talking about your feelings.",
        "You don't have to handle this alone. Let's break down your stressors and tackle them one at a time."
    ],
    "academic_help": [
        "I can help you with academic challenges. What specific subject or concept are you struggling with?",
        "Let's work on your academic goals together. What grade are you aiming for and what's holding you back?",
        "Academic success is about strategy, not just intelligence. Let's develop a plan that works for your learning style.",
        "I've helped many students improve their grades. Let's identify your specific challenges and create targeted solutions."
    ],
    "default": [
        "I'm here to help you succeed. Can you tell me more about what's on your mind?",
        "Let's work together to find a solution. What specific challenge are you facing right now?",
        "I'm here to support you. Feel free to share whatever you're comfortable discussing.",
        "Your success is important to me. How can I best help you today?",
        "I'm listening. Take your time and tell me what you need help with."
    ]
}

def get_ai_response(message):
    """Generate AI response based on message content"""
    message_lower = message.lower()
    
    # Check for specific keywords and return appropriate responses
    if any(word in message_lower for word in ['struggle', 'difficult', 'hard', 'confused', 'don\'t understand', 'stuck']):
        return random.choice(AI_RESPONSES["study_help"])
    elif any(word in message_lower for word in ['give up', 'quit', 'can\'t', 'fail', 'hopeless', 'impossible']):
        return random.choice(AI_RESPONSES["motivation"])
    elif any(word in message_lower for word in ['time', 'schedule', 'plan', 'organize', 'busy', 'overwhelmed', 'stress']):
        return random.choice(AI_RESPONSES["time_management"])
    elif any(word in message_lower for word in ['career', 'job', 'future', 'goals', 'work', 'profession']):
        return random.choice(AI_RESPONSES["career_guidance"])
    elif any(word in message_lower for word in ['stress', 'anxious', 'worried', 'panic', 'pressure']):
        return random.choice(AI_RESPONSES["stress_help"])
    elif any(word in message_lower for word in ['grade', 'study', 'academic', 'class', 'exam', 'test']):
        return random.choice(AI_RESPONSES["academic_help"])
    elif any(word in message_lower for word in ['help', 'support', 'assist', 'guidance']):
        return random.choice(AI_RESPONSES["default"])
    else:
        return random.choice(AI_RESPONSES["default"])

@ai_bp.route('/chat')
@login_required
def ai_chat():
    """AI Chatbot Interface"""
    return render_template('ai_chat.html')

@ai_bp.route('/chat_response', methods=['POST'])
@login_required
def chat_response():
    """Handle AI chat responses"""
    try:
        user_message = request.form.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'response': "I didn't receive your message. Please try again.",
                'timestamp': datetime.datetime.now().isoformat()
            })
        
        # Generate AI response
        ai_response = get_ai_response(user_message)
        
        # Log interaction (in real implementation, save to database)
        interaction = {
            'timestamp': datetime.datetime.now().isoformat(),
            'user_message': user_message,
            'ai_response': ai_response
        }
        
        return jsonify({
            'response': ai_response,
            'timestamp': interaction['timestamp']
        })
        
    except Exception as e:
        # Error handling
        return jsonify({
            'response': "I'm having trouble responding right now. Please try again in a moment.",
            'timestamp': datetime.datetime.now().isoformat(),
            'error': str(e)
        })

@ai_bp.route('/dashboard')
@login_required
def ai_dashboard():
    """AI Dashboard with insights and predictions"""
    # Import here to avoid circular import
    from app_working import db
    
    # Get student data for AI analysis
    try:
        students = db.session.query(Student).all()
    except Exception as e:
        # Fallback if database is not available
        students = []
    
    # Mock AI predictions (in real implementation, use ML models)
    ai_insights = {
        'total_students': len(students),
        'at_risk_count': sum(1 for s in students if s.gpa < 7.0 or s.attendance_percentage < 75),
        'high_performers': sum(1 for s in students if s.gpa >= 8.5 and s.attendance_percentage >= 90),
        'predictions': []
    }
    
    # Create detailed predictions for each student
    for student in students[:5]:  # Show top 5 for demo
        risk_score = 0
        
        # Calculate risk score based on multiple factors
        if student.gpa < 6.0:
            risk_score += 30
        elif student.gpa < 7.0:
            risk_score += 15
            
        if student.attendance_percentage < 70:
            risk_score += 25
        elif student.attendance_percentage < 80:
            risk_score += 10
            
        if hasattr(student, 'mental_health_score') and student.mental_health_score <= 3:
            risk_score += 20
        elif hasattr(student, 'mental_health_score') and student.mental_health_score <= 5:
            risk_score += 10
            
        if hasattr(student, 'financial_stress') and student.financial_stress >= 8:
            risk_score += 15
        elif hasattr(student, 'financial_stress') and student.financial_stress >= 6:
            risk_score += 8
            
        if hasattr(student, 'work_hours_per_week') and student.work_hours_per_week > 30:
            risk_score += 20
        elif hasattr(student, 'work_hours_per_week') and student.work_hours_per_week > 20:
            risk_score += 10
            
        if hasattr(student, 'first_generation') and student.first_generation:
            risk_score += 10
        if hasattr(student, 'previous_dropout') and student.previous_dropout:
            risk_score += 25
        if hasattr(student, 'learning_disability') and student.learning_disability:
            risk_score += 15
        if hasattr(student, 'internet_access') and not student.internet_access:
            risk_score += 20
        if hasattr(student, 'device_access') and not student.device_access:
            risk_score += 15
        
        risk_score = min(100, risk_score)
        
        # Determine risk level
        if risk_score > 70:
            risk_level = 'high'
        elif risk_score > 40:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Determine risk factors
        factors = []
        if student.gpa < 6.0:
            factors.append('Low CGPA')
        if student.attendance_percentage < 70:
            factors.append('Poor Attendance')
        if hasattr(student, 'mental_health_score') and student.mental_health_score <= 3:
            factors.append('Mental Health Issues')
        if hasattr(student, 'financial_stress') and student.financial_stress >= 8:
            factors.append('High Financial Stress')
        if hasattr(student, 'work_hours_per_week') and student.work_hours_per_week > 30:
            factors.append('Excessive Work Hours')
        if hasattr(student, 'first_generation') and student.first_generation:
            factors.append('First Generation')
        if hasattr(student, 'previous_dropout') and student.previous_dropout:
            factors.append('Previous Dropout')
        if hasattr(student, 'learning_disability') and student.learning_disability:
            factors.append('Learning Disability')
        if hasattr(student, 'internet_access') and not student.internet_access:
            factors.append('No Internet Access')
        if hasattr(student, 'device_access') and not student.device_access:
            factors.append('No Device Access')
        
        ai_insights['predictions'].append({
            'student_id': student.student_id,
            'name': f"{student.first_name} {student.last_name}",
            'risk_score': risk_score / 100,  # Convert to 0-1 scale
            'risk_level': risk_level,
            'factors': factors,
            'gpa': student.gpa,
            'attendance': student.attendance_percentage
        })
    
    return render_template('ai_dashboard.html', insights=ai_insights)
