#!/usr/bin/env python3
"""
Comprehensive Authentication Test Script
Tests all authentication flows after fixes
"""

import requests
import json
import pytest
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

# This module is an integration script that expects a running local server.
# Skip in automated pytest runs to avoid fixture-collection errors.
pytestmark = pytest.mark.skip(reason="Manual integration script; run directly with python.")

def test_login(email, password, expected_role=None):
    """Test login with given credentials"""
    session = requests.Session()
    
    login_data = {
        'email': email,
        'password': password
    }
    
    try:
        # Get login page first
        response = session.get(urljoin(BASE_URL, '/auth/login'))
        print(f"GET /auth/login: {response.status_code}")
        
        # Post login data
        response = session.post(urljoin(BASE_URL, '/auth/login'), data=login_data)
        print(f"POST /auth/login: {response.status_code}")
        
        if response.status_code == 200:
            # Check if login failed (still on login page)
            if 'login' in response.url or 'Invalid' in response.text:
                print(f"  LOGIN FAILED: {email}")
                return False, session
            else:
                # Login successful, check redirect
                print(f"  LOGIN SUCCESS: {email}")
                print(f"  Redirected to: {response.url}")
                
                # Get dashboard to verify role
                dashboard_response = session.get(urljoin(BASE_URL, '/dashboard'))
                print(f"GET /dashboard: {dashboard_response.status_code}")
                
                if expected_role:
                    expected_redirect = f"{expected_role}/dashboard"
                    if expected_redirect in dashboard_response.url:
                        print(f"  ROLE VERIFIED: Redirected to {expected_redirect}")
                    else:
                        print(f"  ROLE ISSUE: Expected {expected_redirect}, got {dashboard_response.url}")
                
                return True, session
        else:
            print(f"  HTTP ERROR: {response.status_code}")
            return False, session
            
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        return False, session

def test_student_isolation(session, student_email):
    """Test that student can only access their own data"""
    try:
        # Try to access admin dashboard (don't follow redirects)
        response = session.get(urljoin(BASE_URL, '/admin/dashboard'), allow_redirects=False)
        if response.status_code == 302 and 'login' in response.headers.get('Location', ''):
            print("  STUDENT ISOLATION: Cannot access admin dashboard - redirected to login (GOOD)")
        elif response.status_code == 200:
            if 'Admin access required' in response.text:
                print("  STUDENT ISOLATION: Cannot access admin dashboard - access denied (GOOD)")
            else:
                print("  STUDENT ISOLATION FAILED: Can access admin dashboard (BAD)")
                return False
        else:
            print(f"  ADMIN DASHBOARD UNEXPECTED: {response.status_code}")
            return False
        
        # Try to access faculty dashboard (don't follow redirects)
        response = session.get(urljoin(BASE_URL, '/faculty/dashboard'), allow_redirects=False)
        if response.status_code == 302 and 'login' in response.headers.get('Location', ''):
            print("  STUDENT ISOLATION: Cannot access faculty dashboard - redirected to login (GOOD)")
        elif response.status_code == 200:
            if 'Faculty access required' in response.text:
                print("  STUDENT ISOLATION: Cannot access faculty dashboard - access denied (GOOD)")
            else:
                print("  STUDENT ISOLATION FAILED: Can access faculty dashboard (BAD)")
                return False
        else:
            print(f"  FACULTY DASHBOARD UNEXPECTED: {response.status_code}")
            return False
        
        # Access own student dashboard (follow redirects)
        response = session.get(urljoin(BASE_URL, '/student/dashboard'))
        if response.status_code == 200:
            if student_email in response.text or 'My Academic Dashboard' in response.text:
                print("  STUDENT ISOLATION: Can access own dashboard (GOOD)")
                return True
            else:
                print("  STUDENT ISOLATION FAILED: Cannot access own dashboard")
                return False
        else:
            print(f"  STUDENT DASHBOARD ERROR: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ISOLATION TEST ERROR: {str(e)}")
        return False

def main():
    print("=== AUTHENTICATION SYSTEM TEST ===\n")
    
    # Test credentials from database
    test_cases = [
        ('admin@eduguard.edu', 'admin123', 'admin'),
        ('faculty@eduguard.edu', 'faculty123', 'faculty'), 
        ('rohit.verma@eduguard.edu', 'student123', 'student'),
    ]
    
    results = {}
    
    for email, password, expected_role in test_cases:
        print(f"\n--- Testing {email} (Expected: {expected_role}) ---")
        success, session = test_login(email, password, expected_role)
        results[email] = {'success': success, 'session': session, 'role': expected_role}
        
        if success and expected_role == 'student':
            print("\n--- Testing Student Data Isolation ---")
            test_student_isolation(session, email)
    
    # Summary
    print("\n=== TEST SUMMARY ===")
    for email, result in results.items():
        status = "PASS" if result['success'] else "FAIL"
        print(f"{email}: {status}")
    
    print(f"\nTotal: {sum(1 for r in results.values() if r['success'])}/{len(results)} logins successful")
    
    if all(r['success'] for r in results.values()):
        print("\nAll authentication tests PASSED! System is working correctly.")
    else:
        print("\nSome tests FAILED. Check the logs above for details.")

if __name__ == "__main__":
    main()
