"""
Test login and dashboard functionality
"""

import requests
import json

def test_login_dashboard():
    """Test login and dashboard access"""
    base_url = "http://127.0.0.1:5000"
    
    print("=== LOGIN & DASHBOARD TEST ===")
    
    # Test 1: Check if app is accessible
    print("\n1. APP ACCESSIBILITY")
    try:
        response = requests.get(base_url, timeout=5)
        print(f"   App accessible: {response.status_code == 200}")
        if response.status_code != 200:
            print(f"   Status code: {response.status_code}")
            return
    except Exception as e:
        print(f"   App not accessible: {e}")
        return
    
    # Test 2: Try dashboard access directly
    print("\n2. DASHBOARD DIRECT ACCESS")
    try:
        dashboard_response = requests.get(f"{base_url}/student/dashboard", timeout=5)
        print(f"   Dashboard status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("   Dashboard accessible")
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
            
            # Check for empty indicators
            if "No data" in content or "empty" in content.lower():
                print("   Empty data indicators found")
            else:
                print("   No empty data indicators")
            
            # Check for specific issues
            if "Error" in content:
                print("   Error indicators found")
            if "None" in content:
                print("   None indicators found")
            
            # Save content for analysis
            with open('dashboard_content.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("   Dashboard content saved to dashboard_content.html")
            
        else:
            print(f"   Dashboard access failed: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"   Dashboard test error: {e}")
    
    # Test 3: Try login if needed
    print("\n3. LOGIN FUNCTIONALITY")
    login_data = {
        'email': 'rohit.verma@eduguard.edu',
        'password': 'student123'
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", data=login_data, timeout=5)
        print(f"   Login attempt status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect after successful login
            print("   Login successful (redirect)")
        elif response.status_code == 200:
            print("   Login returned 200 - might be direct dashboard access")
        else:
            print(f"   Login failed: {response.status_code}")
            
    except Exception as e:
        print(f"   Login test error: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == '__main__':
    test_login_dashboard()
