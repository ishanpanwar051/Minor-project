"""
Comprehensive Test Script for EduGuard System
Tests all major functionality end-to-end
"""

import requests
import json
from datetime import datetime

class EduGuardTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_login(self):
        """Test login functionality"""
        print("🔐 Testing Login...")
        
        # Test admin login
        login_data = {
            'email': 'admin@school.edu',
            'password': 'admin123'
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login", data=login_data)
            if response.status_code == 200:
                print("✅ Admin login successful")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_dashboard(self):
        """Test dashboard loading"""
        print("📊 Testing Dashboard...")
        
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            if response.status_code == 200:
                print("✅ Dashboard loaded successfully")
                return True
            else:
                print(f"❌ Dashboard failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
            return False
    
    def test_students_page(self):
        """Test students listing"""
        print("👥 Testing Students Page...")
        
        try:
            response = self.session.get(f"{self.base_url}/students")
            if response.status_code == 200:
                print("✅ Students page loaded successfully")
                return True
            else:
                print(f"❌ Students page failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Students page error: {e}")
            return False
    
    def test_analytics(self):
        """Test analytics page"""
        print("📈 Testing Analytics...")
        
        try:
            response = self.session.get(f"{self.base_url}/analytics")
            if response.status_code == 200:
                print("✅ Analytics loaded successfully")
                return True
            else:
                print(f"❌ Analytics failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Analytics error: {e}")
            return False
    
    def test_prediction(self):
        """Test AI prediction"""
        print("🤖 Testing AI Prediction...")
        
        try:
            # Get prediction page
            response = self.session.get(f"{self.base_url}/predict")
            if response.status_code == 200:
                print("✅ Prediction page loaded successfully")
                return True
            else:
                print(f"❌ Prediction page failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return False
    
    def test_student_detail(self):
        """Test student detail page"""
        print("👤 Testing Student Detail...")
        
        try:
            # Try to access first student's detail page
            response = self.session.get(f"{self.base_url}/student/1")
            if response.status_code == 200:
                print("✅ Student detail loaded successfully")
                return True
            else:
                print(f"❌ Student detail failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Student detail error: {e}")
            return False
    
    def test_logout(self):
        """Test logout functionality"""
        print("🚪 Testing Logout...")
        
        try:
            response = self.session.get(f"{self.base_url}/auth/logout")
            if response.status_code == 200:
                print("✅ Logout successful")
                return True
            else:
                print(f"❌ Logout failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Logout error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting EduGuard System Tests...")
        print("=" * 50)
        
        tests = [
            self.test_login,
            self.test_dashboard,
            self.test_students_page,
            self.test_analytics,
            self.test_prediction,
            self.test_student_detail,
            self.test_logout
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! System is fully functional!")
        else:
            print("⚠️ Some tests failed. Please check the system.")
        
        return passed == total

if __name__ == "__main__":
    tester = EduGuardTester()
    tester.run_all_tests()
