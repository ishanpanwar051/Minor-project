#!/usr/bin/env python3
"""
Chatbot Integration with Main Flask Application
Complete integration of AI chatbot with existing EduGuard system
"""

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from chatbot_routes import chatbot_bp
from ai_chatbot_service import chatbot_service
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///eduguard.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Register chatbot blueprint
app.register_blueprint(chatbot_bp)

# Load user (simplified for demo)
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Main routes
@app.route('/')
def index():
    """Main page with chatbot integration"""
    return render_template('chatbot_frontend.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard with integrated chatbot"""
    return render_template('chatbot_frontend.html')

@app.route('/login')
def login():
    """Simple login for demo"""
    return render_template('login.html')

@app.route('/chatbot')
def chatbot_page():
    """Dedicated chatbot page"""
    return render_template('chatbot_frontend.html')

# API endpoint for testing
@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working"""
    return {
        "status": "success",
        "message": "Chatbot API is working",
        "timestamp": chatbot_service.generate_response("Hello", None)['timestamp']
    }

# Initialize database
def init_db():
    """Initialize database with basic data"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")

if __name__ == '__main__':
    init_db()
    
    print("🤖 Starting AI Chatbot Server")
    print("📱 Chatbot UI: http://127.0.0.1:5000")
    print("🔗 API Endpoint: http://127.0.0.1:5000/api/chat")
    print("📊 Test API: http://127.0.0.1:5000/api/test")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
