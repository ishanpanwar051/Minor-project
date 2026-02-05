"""
Debug Login Issues
Test the login functionality
"""

import requests
import json

def test_login():
    """Test login functionality"""
    base_url = "http://127.0.0.1:5000"
    
    # Test credentials
    credentials = [
        {"email": "admin@eduguard.edu", "password": "admin123"},
        {"email": "faculty@eduguard.edu", "password": "faculty123"},
        {"email": "john.doe@eduguard.edu", "password": "student123"}
    ]
    
    session = requests.Session()
    
    for cred in credentials:
        print(f"\n🔍 Testing login for: {cred['email']}")
        
        # Get login page first
        try:
            response = session.get(f"{base_url}/login")
            print(f"✅ Login page accessible: {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot access login page: {e}")
            continue
        
        # Try to login
        try:
            response = session.post(f"{base_url}/login", data=cred)
            print(f"📝 Login response status: {response.status_code}")
            print(f"📍 Redirected to: {response.url}")
            
            if response.status_code == 302:
                print("✅ Login successful - redirected to dashboard")
                # Follow redirect
                dashboard = session.get(response.headers.get('Location', f"{base_url}/dashboard"))
                print(f"📊 Dashboard status: {dashboard.status_code}")
                break
            elif response.status_code == 200:
                print("❌ Login failed - returned to login page")
                # Check if there are error messages
                if "Invalid email or password" in response.text:
                    print("❌ Error: Invalid credentials")
                else:
                    print("❌ Error: Unknown login issue")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Login request failed: {e}")

if __name__ == '__main__':
    test_login()
