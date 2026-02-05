"""
Debug Login Test for EduGuard System
"""

import requests
import hashlib

def test_login():
    """Test login functionality"""
    
    # Test data
    login_data = {
        'email': 'admin@university.edu',
        'password': 'admin123'
    }
    
    try:
        # Test login endpoint
        response = requests.post('http://127.0.0.1:5000/login', data=login_data)
        
        print(f"🔐 Login Test Results:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"   Redirect Location: {response.headers.get('Location')}")
            print("✅ Login successful - redirecting to dashboard")
        elif response.status_code == 200:
            print("❌ Login failed - returning to login page")
            print("   Response content:")
            print(response.text[:500])  # First 500 characters
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the application. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error testing login: {e}")

if __name__ == '__main__':
    test_login()
