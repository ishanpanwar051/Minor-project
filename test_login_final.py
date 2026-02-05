"""
Test Login Functionality
"""

import requests
import json

def test_login():
    """Test admin login"""
    
    # Test admin login
    login_data = {
        'email': 'admin@university.edu',
        'password': 'admin123'
    }
    
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        
        # Get login page first
        response = session.get('http://127.0.0.1:5000/login')
        print(f"📄 Login page status: {response.status_code}")
        
        # Test login
        response = session.post('http://127.0.0.1:5000/login', data=login_data)
        
        print(f"🔐 Login Test Results:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   ✅ Login successful!")
            print(f"   Redirect Location: {response.headers.get('Location')}")
            
            # Follow redirect
            dashboard_response = session.get('http://127.0.0.1:5000')
            print(f"   Dashboard status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print(f"   ✅ Successfully accessed dashboard!")
                if 'EduGuard' in dashboard_response.text:
                    print(f"   ✅ Dashboard content loaded correctly!")
                else:
                    print(f"   ⚠️ Dashboard may not be loading correctly")
            
        elif response.status_code == 200:
            print(f"   ❌ Login failed - staying on login page")
            if 'Invalid email or password' in response.text:
                print(f"   ❌ Authentication failed")
            else:
                print(f"   ⚠️ Unexpected response")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the application. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error testing login: {e}")

if __name__ == '__main__':
    test_login()
