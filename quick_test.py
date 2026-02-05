"""
Quick Login Test
"""

import requests

def test_login():
    try:
        # Test login
        response = requests.post('http://127.0.0.1:5000/login', data={
            'email': 'admin@university.edu',
            'password': 'admin123'
        })
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 302:
            print("✅ Login successful! Redirecting to dashboard...")
        elif response.status_code == 200:
            print("❌ Login failed - check credentials")
        else:
            print(f"Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_login()
