import requests
from bs4 import BeautifulSoup
import json
import sys

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def login():
    print("--- PHASE 1: LOGIN ---")
    data = {
        'email': 'john.doe@eduguard.edu',
        'password': 'student123'
    }
    try:
        # First get the CSRF token if needed, or simply post
        # The login form might require a csrf token. Let's get the login page first.
        r_get = session.get(f"{BASE_URL}/auth/login")
        soup = BeautifulSoup(r_get.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if csrf_token:
            data['csrf_token'] = csrf_token['value']
        
        r = session.post(f"{BASE_URL}/auth/login", data=data, allow_redirects=True)
        if "Invalid" in r.text or "login" in r.url:
            print(f"❌ Login Failed! URL: {r.url}, Status: {r.status_code}")
            if "Invalid email or password" in r.text:
                print("   Reason: Invalid credentials")
            else:
                print("   Reason: Unknown (check r.text)")
            return False
        print(f"✅ Login Successful! Landed on: {r.url}")
        return True
    except Exception as e:
        print(f"❌ Login Request Failed: {e}")
        return False

def test_endpoint(name, url):
    print(f"\n--- Testing: {name} ---")
    try:
        r = session.get(f"{BASE_URL}{url}")
        if r.status_code == 200:
            print(f"✅ {url} - 200 OK")
            try:
                data = r.json()
                print(f"   Response Preview: {str(data)[:100]}...")
                return True
            except:
                print(f"   (Response is not JSON, length: {len(r.text)})")
                return True
        else:
            print(f"❌ {url} - Failed with status {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing {url}: {e}")
        return False

def check_html_sections():
    print("\n--- Testing: Dashboard HTML Sections ---")
    try:
        r = session.get(f"{BASE_URL}/student_dashboard")
        soup = BeautifulSoup(r.content, 'html.parser')
        
        sections = [
            "Scholarships",
            "AI Insights", 
            "Assistant",
            "Counselling",
            "Applications",
            "Recommendations",
            "GPA",
            "Attendance",
            "Notification"
        ]
        
        text_content = soup.get_text()
        for sec in sections:
            if sec.lower() in text_content.lower():
                print(f"✅ Found section mentioning: {sec}")
            else:
                print(f"❌ Missing section mentioning: {sec}")
                
    except Exception as e:
        print(f"❌ Error fetching dashboard HTML: {e}")

if __name__ == "__main__":
    if not login():
        sys.exit(1)
        
    endpoints = [
        ("Scholarships APIs", "/scholarship/api/scholarships"),
        ("My Applications", "/scholarship/api/my-applications"),
        ("AI Insights", "/ai-dashboard/api/student-insights"),
        ("AI Recommendations", "/ai-assistant/api/recommendations"),
        ("Counselling Analytics", "/counselling/api/analytics")
    ]
    
    for name, url in endpoints:
        test_endpoint(name, url)
        
    check_html_sections()
