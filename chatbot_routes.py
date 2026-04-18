#!/usr/bin/env python3
"""
Chatbot Routes - Flask API endpoints for AI chatbot
Production-ready chatbot with error handling and session management
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from ai_chatbot_service import chatbot_service
from datetime import datetime
import uuid

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api')

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chatbot endpoint
    Accepts: { "message": "user input" }
    Returns: { "reply": "AI response" }
    """
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "status": "error",
                "error_type": "invalid_content_type"
            }), 400
        
        data = request.get_json()
        
        # Validate message
        message = data.get('message', '').strip()
        if not message:
            return jsonify({
                "error": "Message cannot be empty",
                "status": "error", 
                "error_type": "empty_message"
            }), 400
        
        # Get or create session ID
        session_id = session.get('chatbot_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['chatbot_session_id'] = session_id
        
        # Generate response
        response = chatbot_service.generate_response(message, session_id)
        
        # Log the interaction
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Chat: {message[:50]}...")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reply: {response['reply'][:50]}...")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return jsonify({
            "error": "Internal server error",
            "status": "error",
            "error_type": "server_error"
        }), 500

@chatbot_bp.route('/chat/history', methods=['GET'])
@login_required
def chat_history():
    """
    Get conversation history for current session
    """
    try:
        session_id = session.get('chatbot_session_id')
        if not session_id:
            return jsonify({
                "message": "No active session",
                "history": [],
                "status": "no_session"
            })
        
        summary = chatbot_service.get_conversation_summary(session_id)
        return jsonify({
            "status": "success",
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Chat history error: {e}")
        return jsonify({
            "error": "Failed to retrieve chat history",
            "status": "error"
        }), 500

@chatbot_bp.route('/chat/clear', methods=['POST'])
@login_required
def clear_chat():
    """
    Clear conversation history for current session
    """
    try:
        session_id = session.get('chatbot_session_id')
        if session_id:
            chatbot_service.clear_conversation_history(session_id)
            # Generate new session ID
            new_session_id = str(uuid.uuid4())
            session['chatbot_session_id'] = new_session_id
        
        return jsonify({
            "message": "Chat history cleared successfully",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Clear chat error: {e}")
        return jsonify({
            "error": "Failed to clear chat history",
            "status": "error"
        }), 500

@chatbot_bp.route('/chat/status', methods=['GET'])
def chat_status():
    """
    Get chatbot status and configuration
    """
    try:
        return jsonify({
            "status": "online",
            "features": {
                "openai_integration": bool(chatbot_service.api_key),
                "conversation_memory": True,
                "emotional_detection": True,
                "motivational_support": True
            },
            "session_active": bool(session.get('chatbot_session_id')),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Chat status error: {e}")
        return jsonify({
            "error": "Failed to get chatbot status",
            "status": "error"
        }), 500

@chatbot_bp.route('/chat/analyze', methods=['POST'])
@login_required
def analyze_message():
    """
    Analyze user message for emotional state and sentiment
    """
    try:
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400
        
        # Analyze emotional state
        emotional_state = chatbot_service.detect_emotional_state(message)
        
        # Basic sentiment analysis
        positive_words = ['happy', 'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'excited']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry', 'frustrated', 'disappointed', 'sad', 'worried']
        
        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        sentiment = 'neutral'
        if positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > positive_count:
            sentiment = 'negative'
        
        return jsonify({
            "message": message,
            "emotional_state": emotional_state,
            "sentiment": sentiment,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "analysis_timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Message analysis error: {e}")
        return jsonify({
            "error": "Failed to analyze message",
            "status": "error"
        }), 500

# Error handlers for chatbot blueprint
@chatbot_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad request",
        "status": "error",
        "message": "The request was invalid or malformed"
    }), 400

@chatbot_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "error",
        "message": "The requested chatbot endpoint does not exist"
    }), 404

@chatbot_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "status": "error",
        "message": "An unexpected error occurred"
    }), 500
