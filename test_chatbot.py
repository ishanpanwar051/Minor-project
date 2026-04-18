#!/usr/bin/env python3
"""
Test AI Chatbot System - Comprehensive testing of all features
"""

import requests
import json
import time
from ai_chatbot_service import chatbot_service

def test_chatbot_service():
    """Test the chatbot service directly"""
    print("🤖 Testing AI Chatbot Service")
    print("=" * 50)
    
    # Test messages
    test_messages = [
        "Hello, how are you?",
        "I'm feeling stressed about exams",
        "Can you help me study better?",
        "What career should I choose?",
        "I'm so sad and unmotivated",
        "How do I manage my time?",
        "Tell me about yourself",
        "random message with no specific topic"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        print("-" * 40)
        
        # Generate response
        response = chatbot_service.generate_response(message, f"test_session_{i}")
        
        print(f"Status: {response['status']}")
        print(f"Source: {response['source']}")
        print(f"Emotional State: {response.get('emotional_state', 'None')}")
        print(f"Response: {response['reply'][:100]}...")
        
        time.sleep(0.5)  # Small delay between tests

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n\n🌐 Testing API Endpoints")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Chat endpoint
    print("\n1. Testing /api/chat endpoint")
    print("-" * 30)
    
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={"message": "Hello, I need help with studying"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response Status: {data.get('status')}")
            print(f"Reply: {data.get('reply', 'No reply')[:100]}...")
            print("✅ Chat endpoint working")
        else:
            print(f"❌ Chat endpoint failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat endpoint error: {e}")
    
    # Test 2: Status endpoint
    print("\n2. Testing /api/chat/status endpoint")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/chat/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Features: {data.get('features')}")
            print("✅ Status endpoint working")
        else:
            print(f"❌ Status endpoint failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Status endpoint error: {e}")
    
    # Test 3: Analyze endpoint
    print("\n3. Testing /api/chat/analyze endpoint")
    print("-" * 40)
    
    try:
        response = requests.post(
            f"{base_url}/api/chat/analyze",
            json={"message": "I'm feeling very happy and excited about my progress!"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Emotional State: {data.get('emotional_state')}")
            print(f"Sentiment: {data.get('sentiment')}")
            print(f"Positive Words: {data.get('positive_words')}")
            print(f"Negative Words: {data.get('negative_words')}")
            print("✅ Analyze endpoint working")
        else:
            print(f"❌ Analyze endpoint failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Analyze endpoint error: {e}")
    
    # Test 4: Error handling
    print("\n4. Testing Error Handling")
    print("-" * 30)
    
    # Test empty message
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={"message": ""},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Empty message error handling working")
        else:
            print("❌ Empty message error handling failed")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error handling test failed: {e}")
    
    # Test invalid JSON
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Invalid JSON error handling working")
        else:
            print("❌ Invalid JSON error handling failed")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Invalid JSON test failed: {e}")

def test_conversation_memory():
    """Test conversation memory functionality"""
    print("\n\n🧠 Testing Conversation Memory")
    print("=" * 40)
    
    session_id = "test_memory_session"
    
    # Clear any existing history
    chatbot_service.clear_conversation_history(session_id)
    
    # Send multiple messages in conversation
    conversation = [
        "Hi, I'm John",
        "I need help with time management",
        "Can you give me specific tips?",
        "What about the Pomodoro technique?"
    ]
    
    for i, message in enumerate(conversation):
        print(f"\nMessage {i+1}: {message}")
        response = chatbot_service.generate_response(message, session_id)
        print(f"Response: {response['reply'][:80]}...")
    
    # Check conversation summary
    summary = chatbot_service.get_conversation_summary(session_id)
    print(f"\nConversation Summary:")
    print(f"  Total Messages: {summary['message_count']}")
    print(f"  Session Active: {summary['session_active']}")
    
    if summary['message_count'] > 0:
        print("✅ Conversation memory working")
    else:
        print("❌ Conversation memory failed")

def test_emotional_detection():
    """Test emotional state detection"""
    print("\n\n😊 Testing Emotional Detection")
    print("=" * 40)
    
    emotional_test_cases = [
        ("I'm feeling so sad and depressed", "sad"),
        ("I'm really stressed about my exams", "stressed"),
        ("I'm exhausted and tired all the time", "tired"),
        ("I'm confused about what to study", "confused"),
        ("I feel completely unmotivated", "demotivated"),
        ("I'm happy and excited", None)  # Should not detect emotion
    ]
    
    for message, expected_emotion in emotional_test_cases:
        detected_emotion = chatbot_service.detect_emotional_state(message)
        
        if detected_emotion == expected_emotion:
            print(f"✅ '{message}' → {detected_emotion or 'None'}")
        else:
            print(f"❌ '{message}' → Detected: {detected_emotion}, Expected: {expected_emotion}")

def test_fallback_responses():
    """Test fallback response system"""
    print("\n\n🔄 Testing Fallback Responses")
    print("=" * 40)
    
    fallback_tests = [
        ("hello", "greeting"),
        ("help me study", "help"),
        ("how to study for exams", "study"),
        ("motivate me", "motivation"),
        ("I'm stressed", "stress"),
        ("career advice", "career"),
        ("time management tips", "time"),
        ("random message", "default")
    ]
    
    for message, expected_category in fallback_tests:
        response = chatbot_service.get_fallback_response(message)
        
        # Check if response contains relevant keywords
        category_indicators = {
            'greeting': ['hello', 'hi', 'greetings'],
            'help': ['help', 'assist', 'support'],
            'study': ['study', 'strategies', 'techniques'],
            'motivation': ['motivation', 'believe', 'success'],
            'stress': ['stress', 'breathing', 'relax'],
            'career': ['career', 'job', 'professional'],
            'time': ['time', 'schedule', 'manage'],
            'default': ['help', 'assist', 'support']
        }
        
        indicators = category_indicators.get(expected_category, [])
        found_indicator = any(indicator in response.lower() for indicator in indicators)
        
        if found_indicator:
            print(f"✅ '{message}' → Appropriate fallback response")
        else:
            print(f"❌ '{message}' → Inappropriate fallback response")

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Chatbot Testing")
    print("=" * 60)
    
    # Test individual components
    test_chatbot_service()
    test_emotional_detection()
    test_fallback_responses()
    test_conversation_memory()
    
    # Test API endpoints (requires server running)
    print("\n\n" + "=" * 60)
    print("📡 Note: API endpoint tests require server to be running")
    print("Start server with: python chatbot_integration.py")
    print("Then run this test again to test API endpoints")
    print("=" * 60)
    
    # Test API if server is running
    try:
        test_api_endpoints()
    except:
        print("⚠️  Skipping API tests - server not running")
    
    print("\n\n🎯 Testing Complete!")
    print("=" * 30)
    print("Check the results above for any issues.")
    print("All tests should show ✅ for proper functionality.")

if __name__ == '__main__':
    main()
