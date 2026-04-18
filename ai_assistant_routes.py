"""
AI Assistant Routes
Intelligent chat-based assistant for students
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from models_enhanced import db, AIInteraction, Student, Scholarship, ScholarshipApplication
from datetime import datetime
import json
import re
from rbac_system import student_required, get_student_for_current_user

ai_assistant_bp = Blueprint('ai_assistant', __name__, url_prefix='/ai-assistant')

# ================================
# AI Assistant Chat Interface
# ================================

@ai_assistant_bp.route('/')
@login_required
@student_required
def chat_interface():
    """AI Assistant chat interface"""
    student = get_student_for_current_user()
    if not student:
        return redirect(url_for('auth.login'))
    
    # Get recent chat history
    session_id = session.get('chat_session_id', str(datetime.utcnow().timestamp()))
    session['chat_session_id'] = session_id
    
    recent_interactions = AIInteraction.query.filter_by(
        user_id=current_user.id,
        session_id=session_id
    ).order_by(AIInteraction.timestamp.desc()).limit(20).all()
    
    return render_template('ai_assistant/chat.html', 
                         student=student,
                         recent_interactions=recent_interactions)

@ai_assistant_bp.route('/api/chat', methods=['POST'])
@login_required
@student_required
def api_chat():
    """API endpoint for AI Assistant chat"""
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    session_id = session.get('chat_session_id', str(datetime.utcnow().timestamp()))
    session['chat_session_id'] = session_id
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    student = get_student_for_current_user()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Process user message and generate response
    start_time = datetime.utcnow()
    
    # Classify intent
    intent, confidence = classify_intent(user_message)
    
    # Generate context-aware response
    response_data = generate_ai_response(user_message, student, intent, session_id)
    
    # Calculate response time
    response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    # Log interaction
    interaction = AIInteraction(
        user_id=current_user.id,
        session_id=session_id,
        interaction_type='query',
        user_query=user_message,
        ai_response=response_data['response'],
        context_data=json.dumps({
            'student_id': student.id,
            'intent': intent,
            'confidence': confidence
        }),
        intent_classification=intent,
        confidence_score=confidence,
        response_time_ms=int(response_time)
    )
    
    db.session.add(interaction)
    db.session.commit()
    
    return jsonify(response_data)

@ai_assistant_bp.route('/api/recommendations')
@login_required
@student_required
def api_recommendations():
    """Get personalized scholarship recommendations"""
    
    student = get_student_for_current_user()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    recommendations = get_scholarship_recommendations(student)
    
    return jsonify({
        'recommendations': recommendations,
        'total_scholarships': len(recommendations)
    })

@ai_assistant_bp.route('/api/feedback', methods=['POST'])
@login_required
@student_required
def api_feedback():
    """Submit feedback for AI response"""
    
    data = request.get_json()
    interaction_id = data.get('interaction_id')
    rating = data.get('rating')  # 1-5
    feedback_text = data.get('feedback', '')
    
    if not interaction_id or not rating:
        return jsonify({'error': 'Interaction ID and rating are required'}), 400
    
    interaction = AIInteraction.query.get_or_404(interaction_id)
    
    # Verify ownership
    if interaction.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    interaction.response_quality_rating = rating
    interaction.feedback = feedback_text
    interaction.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True})

# ================================
# AI Processing Functions
# ================================

def classify_intent(message):
    """Classify user intent using keyword-based approach"""
    
    message_lower = message.lower()
    
    # Scholarship-related intents
    if any(word in message_lower for word in ['scholarship', 'scholarships', 'award', 'financial aid']):
        if any(word in message_lower for word in ['eligible', 'qualify', 'can i apply']):
            return 'scholarship_eligibility', 0.9
        elif any(word in message_lower for word in ['apply', 'application', 'how to']):
            return 'scholarship_application', 0.9
        elif any(word in message_lower for word in ['recommend', 'suggest', 'find']):
            return 'scholarship_recommendation', 0.9
        elif any(word in message_lower for word in ['deadline', 'due date', 'when']):
            return 'scholarship_deadline', 0.8
        else:
            return 'scholarship_general', 0.8
    
    # Academic-related intents
    elif any(word in message_lower for word in ['gpa', 'grade', 'academic', 'performance']):
        if any(word in message_lower for word in ['improve', 'increase', 'better']):
            return 'academic_improvement', 0.9
        else:
            return 'academic_general', 0.8
    
    # Career-related intents
    elif any(word in message_lower for word in ['career', 'job', 'future', 'profession']):
        if any(word in message_lower for word in ['advice', 'guidance', 'suggest']):
            return 'career_guidance', 0.9
        else:
            return 'career_general', 0.8
    
    # Application-related intents
    elif any(word in message_lower for word in ['application', 'apply', 'submitted', 'status']):
        if any(word in message_lower for word in ['track', 'status', 'check']):
            return 'application_status', 0.9
        elif any(word in message_lower for word in ['help', 'tips', 'improve']):
            return 'application_help', 0.9
        else:
            return 'application_general', 0.8
    
    # General help
    elif any(word in message_lower for word in ['help', 'assist', 'support', 'guidance']):
        return 'general_help', 0.8
    
    # Greeting
    elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return 'greeting', 0.9
    
    # Thanks
    elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return 'thanks', 0.9
    
    else:
        return 'general_query', 0.5

def generate_ai_response(message, student, intent, session_id):
    """Generate context-aware AI response"""
    
    # Get student context
    student_context = get_student_context(student)
    
    # Generate response based on intent
    if intent == 'scholarship_eligibility':
        response = handle_scholarship_eligibility(message, student, student_context)
    elif intent == 'scholarship_application':
        response = handle_scholarship_application(message, student, student_context)
    elif intent == 'scholarship_recommendation':
        response = handle_scholarship_recommendation(message, student, student_context)
    elif intent == 'scholarship_deadline':
        response = handle_scholarship_deadline(message, student, student_context)
    elif intent == 'scholarship_general':
        response = handle_scholarship_general(message, student, student_context)
    elif intent == 'academic_improvement':
        response = handle_academic_improvement(message, student, student_context)
    elif intent == 'academic_general':
        response = handle_academic_general(message, student, student_context)
    elif intent == 'career_guidance':
        response = handle_career_guidance(message, student, student_context)
    elif intent == 'career_general':
        response = handle_career_general(message, student, student_context)
    elif intent == 'application_status':
        response = handle_application_status(message, student, student_context)
    elif intent == 'application_help':
        response = handle_application_help(message, student, student_context)
    elif intent == 'application_general':
        response = handle_application_general(message, student, student_context)
    elif intent == 'general_help':
        response = handle_general_help(message, student, student_context)
    elif intent == 'greeting':
        response = handle_greeting(message, student, student_context)
    elif intent == 'thanks':
        response = handle_thanks(message, student, student_context)
    else:
        response = handle_general_query(message, student, student_context)
    
    return response

def get_student_context(student):
    """Get comprehensive student context for AI responses"""
    
    # Get student's applications
    applications = ScholarshipApplication.query.filter_by(student_id=student.id).all()
    
    # Get eligible scholarships
    from scholarship_routes import is_student_eligible
    eligible_scholarships = []
    for scholarship in Scholarship.query.filter_by(status='active').all():
        if is_student_eligible(student, scholarship):
            eligible_scholarships.append(scholarship)
    
    return {
        'student': student,
        'applications': applications,
        'eligible_scholarships_count': len(eligible_scholarships),
        'pending_applications': len([app for app in applications if app.status.value == 'pending']),
        'approved_applications': len([app for app in applications if app.status.value == 'approved']),
        'gpa': student.gpa or 0,
        'department': student.department or 'Not specified',
        'year': student.year or 1,
        'financial_need': student.financial_need_level or 'Not specified'
    }

# ================================
# Intent Handlers
# ================================

def handle_scholarship_eligibility(message, student, context):
    """Handle scholarship eligibility queries"""
    
    gpa = context['gpa']
    department = context['department']
    year = context['year']
    
    response = f"Based on your profile (GPA: {gpa}, Department: {department}, Year: {year}), "
    
    if gpa >= 3.5:
        response += "you're eligible for most scholarships including those with high GPA requirements. "
    elif gpa >= 3.0:
        response += "you're eligible for many scholarships with moderate GPA requirements. "
    else:
        response += "you should focus on scholarships with lower GPA requirements or need-based awards. "
    
    eligible_count = context['eligible_scholarships_count']
    response += f"I found {eligible_count} scholarships you're currently eligible for. "
    
    if eligible_count > 0:
        response += "Would you like me to show you the best matches?"
    
    return {
        'response': response,
        'suggestions': [
            'Show me eligible scholarships',
            'What scholarships match my GPA?',
            'How can I improve my eligibility?'
        ],
        'actions': [
            {
                'type': 'recommendation',
                'label': 'View Recommended Scholarships',
                'url': '/ai-assistant/api/recommendations'
            }
        ]
    }

def handle_scholarship_application(message, student, context):
    """Handle scholarship application queries"""
    
    pending = context['pending_applications']
    
    response = f"You currently have {pending} pending application{'s' if pending != 1 else ''}. "
    
    if pending > 0:
        response += "For strong applications, I recommend: "
        response += "1) Writing a compelling personal statement that highlights your unique qualities, "
        response += "2) Providing specific examples of your achievements, "
        response += "3) Tailoring each application to the scholarship's requirements, "
        response += "4) Proofreading carefully for any errors. "
    else:
        response += "When you're ready to apply, focus on scholarships that match your profile closely. "
    
    response += "Would you like specific tips for a particular scholarship?"
    
    return {
        'response': response,
        'suggestions': [
            'How to write a strong personal statement',
            'What documents do I need?',
            'Application deadline reminders'
        ]
    }

def handle_scholarship_recommendation(message, student, context):
    """Handle scholarship recommendation requests"""
    
    from ai_dashboard_routes import get_personalized_recommendations
    
    recommendations = get_personalized_recommendations(student)
    
    if recommendations:
        response = f"I found {len(recommendations)} scholarships that are great matches for you. "
        
        # Top 3 recommendations
        top_recommendations = recommendations[:3]
        response += "Here are my top recommendations:\n\n"
        
        for i, rec in enumerate(top_recommendations, 1):
            scholarship = rec['scholarship']
            response += f"{i}. **{scholarship.title}** - ${scholarship.amount:,.0f}\n"
            response += f"   {rec['reason']}\n\n"
        
        response += "Would you like more details about any of these scholarships?"
    else:
        response = "I don't see any active scholarships that match your current profile. "
        response += "Consider improving your GPA or gaining more experience to expand your options."
    
    return {
        'response': response,
        'suggestions': [
            'Show application deadlines',
            'Eligibility requirements',
            'How to improve my profile'
        ],
        'scholarships': [rec['scholarship'].id for rec in recommendations[:5]]
    }

def handle_scholarship_deadline(message, student, context):
    """Handle scholarship deadline queries"""
    
    # Get upcoming deadlines
    upcoming_deadlines = Scholarship.query.filter(
        Scholarship.status == 'active',
        Scholarship.application_deadline > datetime.utcnow()
    ).order_by(Scholarship.application_deadline).limit(5).all()
    
    if upcoming_deadlines:
        response = "Here are upcoming scholarship deadlines:\n\n"
        
        for scholarship in upcoming_deadlines:
            days_left = (scholarship.application_deadline - datetime.utcnow()).days
            response += f"**{scholarship.title}** - {scholarship.application_deadline.strftime('%B %d, %Y')} ({days_left} days left)\n"
        
        response += "\nWould you like me to remind you about these deadlines?"
    else:
        response = "There are no upcoming scholarship deadlines at the moment. "
        response += "Check back regularly for new opportunities."
    
    return {
        'response': response,
        'suggestions': [
            'Set deadline reminders',
            'Show scholarships closing soon',
            'Application timeline help'
        ]
    }

def handle_scholarship_general(message, student, context):
    """Handle general scholarship queries"""
    
    response = "Scholarships are a great way to fund your education! "
    response += "They're typically based on academic merit, financial need, or specific talents. "
    response += f"With your GPA of {context['gpa']}, you have good options available. "
    
    response += "Key tips for scholarship success:\n"
    response += "1) Start early and apply often\n"
    response += "2) Focus on scholarships matching your profile\n"
    response += "3) Write compelling personal statements\n"
    response += "4) Keep track of all deadlines\n\n"
    
    response += "What specific aspect of scholarships would you like to know more about?"
    
    return {
        'response': response,
        'suggestions': [
            'Types of scholarships',
            'How to find scholarships',
            'Application strategies',
            'Success stories'
        ]
    }

def handle_academic_improvement(message, student, context):
    """Handle academic improvement queries"""
    
    gpa = context['gpa']
    
    response = f"Your current GPA is {gpa}. "
    
    if gpa >= 3.5:
        response += "Excellent work! To maintain or improve: "
        response += "continue challenging yourself with advanced courses, "
        response += "seek research opportunities, and maintain strong study habits."
    elif gpa >= 3.0:
        response += "Good progress! To reach the next level: "
        response += "focus on understanding concepts deeply, "
        response += "form study groups, and seek help when needed."
    else:
        response += "There's room for improvement! Consider: "
        response += "meeting with academic advisors, "
        response += "utilizing tutoring services, "
        response += "and developing better time management skills."
    
    response += " Would you like specific study strategies for your courses?"
    
    return {
        'response': response,
        'suggestions': [
            'Study techniques',
            'Time management tips',
            'Course selection advice',
            'Academic resources'
        ]
    }

def handle_academic_general(message, student, context):
    """Handle general academic queries"""
    
    response = f"Your academic profile shows {context['department']} major in year {context['year']}. "
    
    if context['gpa'] >= 3.0:
        response += "You're performing well academically. "
    else:
        response += "There's opportunity for academic growth. "
    
    response += "Focus on building strong foundations in your major courses "
    response += "while exploring electives that interest you. "
    
    return {
        'response': response,
        'suggestions': [
            'Course recommendations',
            'Study strategies',
            'Academic planning',
            'Career preparation'
        ]
    }

def handle_career_guidance(message, student, context):
    """Handle career guidance queries"""
    
    from ai_dashboard_routes import get_career_suggestions
    
    career_suggestions = get_career_suggestions(student)
    
    response = f"Based on your {context['department']} background, here are some career paths:\n\n"
    
    for suggestion in career_suggestions[:3]:
        response += f"**{suggestion['field']}** - {suggestion['reason']}\n"
    
    response += "\nTo prepare for these careers, consider: "
    response += "internships, networking events, and relevant certifications. "
    
    return {
        'response': response,
        'suggestions': [
            'Internship opportunities',
            'Skill development',
            'Networking strategies',
            'Resume building'
        ]
    }

def handle_career_general(message, student, context):
    """Handle general career queries"""
    
    response = "Career planning is an important part of your academic journey. "
    response += "Start by exploring different options within your field, "
    response += "gaining practical experience through internships, "
    response += "and building a professional network. "
    
    return {
        'response': response,
        'suggestions': [
            'Career assessment',
            'Industry insights',
            'Professional development',
            'Job market trends'
        ]
    }

def handle_application_status(message, student, context):
    """Handle application status queries"""
    
    pending = context['pending_applications']
    approved = context['approved_applications']
    
    response = f"Application Status Summary:\n"
    response += f"Pending: {pending}\n"
    response += f"Approved: {approved}\n\n"
    
    if pending > 0:
        response += "You have pending applications under review. "
        response += "Review committees typically take 2-4 weeks to process applications. "
    
    if approved > 0:
        response += f"Congratulations on your {approved} approved application{'s' if approved != 1 else ''}! "
    
    if pending == 0 and approved == 0:
        response += "You haven't submitted any applications yet. "
        response += "Would you like help finding scholarships to apply for?"
    
    return {
        'response': response,
        'suggestions': [
            'View application details',
            'Application timeline',
            'Next steps',
            'Find new scholarships'
        ]
    }

def handle_application_help(message, student, context):
    """Handle application help queries"""
    
    response = "Here are my top application tips:\n\n"
    response += "1. **Personal Statement**: Tell your unique story with specific examples\n"
    response += "2. **Academic Achievement**: Highlight relevant coursework and projects\n"
    response += "3. **Extracurriculars**: Show leadership and community involvement\n"
    response += "4. **Financial Need**: Clearly explain your situation if applicable\n"
    response += "5. **Proofread**: Check for errors and ask others to review\n\n"
    
    response += "Would you like help with any specific part of the application?"
    
    return {
        'response': response,
        'suggestions': [
            'Personal statement help',
            'Document requirements',
            'Common mistakes to avoid',
            'Success examples'
        ]
    }

def handle_application_general(message, student, context):
    """Handle general application queries"""
    
    response = "The scholarship application process typically involves: "
    response += "researching opportunities, preparing documents, writing personal statements, "
    response += "and submitting before deadlines. "
    
    return {
        'response': response,
        'suggestions': [
            'Application process overview',
            'Required documents',
        'Timeline planning',
        'Common requirements'
        ]
    }

def handle_general_help(message, student, context):
    """Handle general help queries"""
    
    response = "I'm here to help you with scholarships, academics, and career planning! "
    response += "I can assist with:\n\n"
    response += "Finding scholarships you're eligible for\n"
    response += "Application guidance and tips\n"
    response += "Academic improvement strategies\n"
    response += "Career path exploration\n"
    response += "Deadline tracking and reminders\n\n"
    
    response += "What would you like help with today?"
    
    return {
        'response': response,
        'suggestions': [
            'Scholarship search',
            'Application help',
            'Academic advice',
            'Career guidance'
        ]
    }

def handle_greeting(message, student, context):
    """Handle greeting messages"""
    
    greetings = [
        f"Hello {student.first_name}! I'm your AI assistant, ready to help with scholarships and academic guidance.",
        f"Hi {student.first_name}! How can I assist you with your educational journey today?",
        f"Welcome back, {student.first_name}! What can I help you with today?"
    ]
    
    import random
    response = random.choice(greetings)
    
    return {
        'response': response,
        'suggestions': [
            'Find scholarships',
            'Check application status',
            'Academic advice',
            'Career guidance'
        ]
    }

def handle_thanks(message, student, context):
    """Handle thank you messages"""
    
    responses = [
        "You're welcome! I'm always here to help.",
        "Happy to assist! Don't hesitate to reach out anytime.",
        "My pleasure! Is there anything else I can help you with?",
        "Glad I could help! Let me know if you need further assistance."
    ]
    
    import random
    response = random.choice(responses)
    
    return {
        'response': response,
        'suggestions': [
            'More questions',
            'New topic',
            'End chat',
            'Rate this response'
        ]
    }

def handle_general_query(message, student, context):
    """Handle general queries"""
    
    response = "I understand you're looking for information. "
    response += "I can help you with scholarships, applications, academic advice, and career guidance. "
    response += "Could you please be more specific about what you'd like to know?"
    
    return {
        'response': response,
        'suggestions': [
            'Scholarship information',
            'Application help',
            'Academic guidance',
            'Career advice'
        ]
    }

def get_scholarship_recommendations(student):
    """Get scholarship recommendations for API"""
    
    from ai_dashboard_routes import get_personalized_recommendations
    
    recommendations = get_personalized_recommendations(student)
    
    result = []
    for rec in recommendations:
        scholarship = rec['scholarship']
        result.append({
            'id': scholarship.id,
            'title': scholarship.title,
            'provider': scholarship.provider,
            'amount': scholarship.amount,
            'deadline': scholarship.application_deadline.isoformat(),
            'score': rec['score'],
            'reason': rec['reason']
        })
    
    return result
