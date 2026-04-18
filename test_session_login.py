"""
Test session-based login functionality
"""

import requests
import json

def test_session_login():
    """Test login with proper session management"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== SESSION LOGIN TEST ===")
    
    # Create a session object to maintain cookies
    session = requests.Session()
    
    # Test 1: Login with session
    print("\n1. LOGIN WITH SESSION")
    login_data = {
        'email': 'rohit.verma@eduguard.edu',
        'password': 'student123'
    }
    
    try:
        # First, get the login page
        login_page = session.get(f"{base_url}/auth/login", timeout=5)
        print(f"   Login page status: {login_page.status_code}")
        
        # Then submit the login form
        response = session.post(f"{base_url}/auth/login", data=login_data, timeout=5)
        print(f"   Login post status: {response.status_code}")
        
        if response.status_code == 302:
            print("   Login successful (redirect)")
            # Follow the redirect
            dashboard_response = session.get(response.headers.get('Location', f"{base_url}/student/dashboard"), timeout=5)
            print(f"   Dashboard redirect status: {dashboard_response.status_code}")
        elif response.status_code == 200:
            print("   Login returned 200 - checking if dashboard is returned")
            content = response.text
            
            if "Welcome back" in content:
                print("   Dashboard content found in login response")
            elif "Login" in content:
                print("   Still showing login page - login failed")
            else:
                print("   Unknown content returned")
        else:
            print(f"   Login failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"   Login test error: {e}")
        return
    
    # Test 2: Access dashboard with session
    print("\n2. DASHBOARD WITH SESSION")
    try:
        dashboard_response = session.get(f"{base_url}/student/dashboard", timeout=5)
        print(f"   Dashboard status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            content = dashboard_response.text
            
            # Check for key elements
            if "Welcome back" in content:
                print("   Welcome message found")
            else:
                print("   Welcome message NOT found")
            
            if "scholarship" in content.lower():
                print("   Scholarship content found")
            else:
                print("   Scholarship content NOT found")
            
            if "counselling" in content.lower():
                print("   Counselling content found")
            else:
                print("   Counselling content NOT found")
            
            if "Login" in content:
                print("   Still showing login page - authentication failed")
            
            # Save content for analysis
            with open('session_dashboard.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("   Dashboard content saved to session_dashboard.html")
            
        else:
            print(f"   Dashboard access failed: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"   Dashboard test error: {e}")
    
    # Test 3: Check session cookies
    print("\n3. SESSION COOKIES")
    cookies = session.cookies.get_dict()
    print(f"   Session cookies: {cookies}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == '__main__':
    test_session_login()
