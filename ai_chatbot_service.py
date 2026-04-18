#!/usr/bin/env python3
"""
AI Chatbot Service - Smart Conversational AI with Motivational Support
Integrates with OpenAI API and provides intelligent fallback responses
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import re

class AIChatbotService:
    """Intelligent AI Chatbot with multiple response strategies"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.conversation_history = {}  # Session-based memory
        self.max_history = 10  # Keep last 10 messages per session
        
        # Motivational keywords for emotional detection
        self.motivational_keywords = {
            'sad': ['sad', 'depressed', 'unhappy', 'down', 'blue', 'low', 'miserable'],
            'stressed': ['stressed', 'overwhelmed', 'anxious', 'worried', 'tense', 'pressure'],
            'tired': ['tired', 'exhausted', 'fatigued', 'burnout', 'weary', 'drained'],
            'confused': ['confused', 'lost', 'uncertain', 'unsure', 'clueless', 'puzzled'],
            'demotivated': ['demotivated', 'unmotivated', 'lazy', 'procrastinate', 'no energy']
        }
        
        # Smart fallback responses
        self.fallback_responses = {
            'greeting': [
                "Hello! I'm here to help you. How can I assist you today?",
                "Hi there! I'm your AI assistant. What's on your mind?",
                "Greetings! How can I support you today?"
            ],
            'help': [
                "I can help you with study strategies, time management, career guidance, and motivation. What specific area would you like assistance with?",
                "I'm here to support your academic journey. I can help with studying, motivation, career planning, and personal development. What do you need help with?",
                "I'm your AI assistant for student success. I can provide study tips, motivational support, career advice, and academic guidance. How can I help?"
            ],
            'study': [
                "Here are some effective study strategies:\n1. Use the Pomodoro Technique (25 min study, 5 min break)\n2. Create a structured study schedule\n3. Use active recall instead of passive reading\n4. Practice with past papers\n5. Study in a distraction-free environment",
                "For better studying, try these methods:\n• Break large topics into smaller chunks\n• Use spaced repetition for memory\n• Teach concepts to others\n• Create mind maps and visual aids\n• Take regular breaks to maintain focus"
            ],
            'computer_science': [
                "Computer Science Career Path:\n\n**Popular Specializations:**\n• Software Development\n• Data Science/AI\n• Cybersecurity\n• Web Development\n• Mobile Development\n• Cloud Computing\n\n**Key Skills to Develop:**\n• Programming (Python, Java, JavaScript)\n• Data Structures & Algorithms\n• Database Management\n• System Design\n• Problem Solving\n\n**Career Opportunities:**\n• Software Engineer ($70K-150K)\n• Data Scientist ($80K-180K)\n• Cybersecurity Analyst ($65K-130K)\n• Full Stack Developer ($75K-140K)\n\n**Next Steps:**\n1. Start with fundamentals (Python/Java)\n2. Build personal projects\n3. Get certifications (AWS, Google)\n4. Join coding communities\n5. Apply for internships"
            ],
            'programming': [
                "Programming Learning Path:\n\n**Beginner Steps:**\n1. Choose your first language (Python recommended)\n2. Learn basic syntax and concepts\n3. Practice with simple problems\n4. Build small projects\n\n**Intermediate Skills:**\n• Data structures (arrays, lists, trees)\n• Algorithms (sorting, searching)\n• Object-oriented programming\n• Database basics\n\n**Advanced Topics:**\n• System design\n• Machine learning\n• Cloud platforms\n• DevOps\n\n**Resources:**\n• Free: Codecademy, freeCodeCamp, YouTube\n• Paid: Coursera, Udemy, Bootcamps\n• Practice: LeetCode, HackerRank, GitHub"
            ],
            'career': [
                "Career planning advice:\n1. Identify your interests and strengths through self-reflection\n2. Research different career options that match your profile\n3. Talk to professionals in fields that interest you\n4. Gain relevant skills through courses and internships\n5. Build a professional network through LinkedIn and events\n6. Create a compelling resume and portfolio"
            ],
            'motivation': [
                "Remember: Every expert was once a beginner. Keep going, you're making progress even when it doesn't feel like it!",
                "Success is not final, failure is not fatal: it is the courage to continue that counts. You've got this!",
                "The secret of getting ahead is getting started. Take that first step, no matter how small.",
                "Believe you can and you're halfway there. Your potential is limitless!"
            ],
            'stress': [
                "Stress management tips:\n1. Practice deep breathing exercises (4-7-8 technique)\n2. Take regular breaks and stretch\n3. Exercise regularly - even 15 minutes helps\n4. Get 7-8 hours of quality sleep\n5. Talk to friends, family, or counselors\n6. Break large tasks into smaller, manageable steps",
                "When feeling overwhelmed, try this:\n• Pause and take 3 deep breaths\n• Write down everything that's stressing you\n• Prioritize what's most important\n• Ask for help when needed\n• Remember: it's okay to not be okay sometimes"
            ],
            'time': [
                "Time management strategies:\n1. Use a digital calendar or planner\n2. Prioritize tasks using the Eisenhower Matrix (Urgent/Important)\n3. Break large projects into smaller milestones\n4. Use time-blocking for focused work\n5. Eliminate distractions (turn off notifications)\n6. Review and adjust your schedule weekly"
            ],
            'default': [
                "I'm here to help! Could you tell me more about what you need assistance with? I can help with studying, motivation, career planning, and stress management.",
                "I'd be happy to help you! Whether you need study tips, motivational support, or career advice, I'm here for you. What specific challenge are you facing?",
                "I'm your AI assistant dedicated to your success. Feel free to ask me anything about studying, motivation, career planning, or personal development."
            ]
        }
    
    def detect_emotional_state(self, message: str) -> Optional[str]:
        """
        Detect user's emotional state from message
        """
        message_lower = message.lower()
        
        for emotion, keywords in self.motivational_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return emotion
        
        return None
    
    def get_fallback_response(self, message: str) -> str:
        """
        Generate intelligent fallback response based on message content
        """
        message_lower = message.lower()
        
        # Check for greeting
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return self._get_random_response('greeting')
        
        # Check for help request
        if any(word in message_lower for word in ['help', 'assist', 'support', 'guide']):
            return self._get_random_response('help')
        
        # Check for computer science related queries
        if any(word in message_lower for word in ['computer science', 'cs', 'programming', 'coding', 'software', 'developer', 'code']):
            if 'computer science' in message_lower or 'cs' in message_lower:
                return self._get_random_response('computer_science')
            elif any(word in message_lower for word in ['programming', 'coding', 'code']):
                return self._get_random_response('programming')
        
        # Check for study-related queries
        if any(word in message_lower for word in ['study', 'learn', 'exam', 'test', 'homework', 'assignment']):
            return self._get_random_response('study')
        
        # Check for motivational needs
        if any(word in message_lower for word in ['motivate', 'encourage', 'inspire', 'motivation']):
            return self._get_random_response('motivation')
        
        # Check for stress-related queries
        if any(word in message_lower for word in ['stress', 'anxious', 'overwhelmed', 'pressure']):
            return self._get_random_response('stress')
        
        # Check for career-related queries
        if any(word in message_lower for word in ['career', 'job', 'future', 'profession', 'work']):
            return self._get_random_response('career')
        
        # Check for time management queries
        if any(word in message_lower for word in ['time', 'schedule', 'plan', 'organize', 'manage']):
            return self._get_random_response('time')
        
        # Default response
        return self._get_random_response('default')
    
    def _get_random_response(self, category: str) -> str:
        """Get a random response from a category"""
        import random
        return random.choice(self.fallback_responses.get(category, self.fallback_responses['default']))
    
    def call_openai_api(self, message: str, session_id: str = None) -> Optional[str]:
        """
        Call OpenAI API for intelligent response
        """
        if not self.api_key:
            return None
        
        try:
            # Build conversation context
            messages = []
            
            # Add system message
            system_message = {
                "role": "system",
                "content": """You are an AI assistant specializing in student support and motivation. 
                You provide helpful, encouraging, and practical advice for academic success, 
                stress management, career planning, and personal development. 
                Be empathetic, supportive, and provide actionable advice. 
                Keep responses concise but comprehensive."""
            }
            messages.append(system_message)
            
            # Add conversation history if available
            if session_id and session_id in self.conversation_history:
                for msg in self.conversation_history[session_id][-6:]:  # Last 6 messages
                    messages.append(msg)
            
            # Add current message
            user_message = {
                "role": "user",
                "content": message
            }
            messages.append(user_message)
            
            # Make API call
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Store in conversation history
                self._store_conversation(session_id, user_message, {"role": "assistant", "content": ai_response})
                
                return ai_response
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
    
    def _store_conversation(self, session_id: str, user_message: dict, ai_response: dict):
        """Store conversation in session memory"""
        if not session_id:
            return
            
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Add messages
        self.conversation_history[session_id].append(user_message)
        self.conversation_history[session_id].append(ai_response)
        
        # Keep only last N messages
        if len(self.conversation_history[session_id]) > self.max_history * 2:
            self.conversation_history[session_id] = self.conversation_history[session_id][-self.max_history * 2:]
    
    def generate_response(self, message: str, session_id: str = None) -> Dict[str, any]:
        """
        Generate intelligent response to user message
        """
        # Validate input
        if not message or not message.strip():
            return {
                "reply": "Please enter a message. I'm here to help you!",
                "status": "error",
                "error_type": "empty_input"
            }
        
        # Detect emotional state
        emotional_state = self.detect_emotional_state(message)
        
        # Try OpenAI API first
        ai_response = self.call_openai_api(message, session_id)
        
        if ai_response:
            response = ai_response
            response_source = "openai"
        else:
            # Use intelligent fallback
            response = self.get_fallback_response(message)
            response_source = "fallback"
        
        # Add motivational touch if user seems to need it
        if emotional_state:
            motivational_touch = self._get_motivational_touch(emotional_state)
            response += f"\n\n{motivational_touch}"
        
        return {
            "reply": response,
            "status": "success",
            "source": response_source,
            "emotional_state": emotional_state,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_motivational_touch(self, emotional_state: str) -> str:
        """Add motivational touch based on emotional state"""
        motivational_messages = {
            'sad': "Remember, it's okay to feel sad sometimes. You're stronger than you think, and this feeling will pass. 💙",
            'stressed': "Take a deep breath. You've handled challenges before, and you'll get through this one too. You've got this! 💪",
            'tired': "Rest is not a luxury, it's a necessity. Take care of yourself - you deserve it! 🌟",
            'confused': "It's okay to feel uncertain. Every expert was once a beginner. Take it one step at a time. 🎯",
            'demotivated': "Motivation comes from action. Take one small step today, and momentum will follow. 🚀"
        }
        
        return motivational_messages.get(emotional_state, "")
    
    def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, any]:
        """Get summary of conversation"""
        if session_id not in self.conversation_history:
            return {"message_count": 0, "session_active": False}
        
        history = self.conversation_history[session_id]
        return {
            "message_count": len(history),
            "session_active": True,
            "last_message": history[-1] if history else None
        }

# Global instance
chatbot_service = AIChatbotService()
