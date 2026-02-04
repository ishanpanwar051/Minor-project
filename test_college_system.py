"""
College System Test Script for EduGuard
Tests college-specific functionality
"""

import requests
import json
from datetime import datetime

class CollegeSystemTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_college_dashboard(self):
        """Test college dashboard with college-specific data"""
        print("🎓 Testing College Dashboard...")
        
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            if response.status_code == 200:
                print("✅ College dashboard loaded successfully")
                # Check if college-specific content is present
                if 'College Dashboard' in response.text:
                    print("✅ College-specific branding found")
                return True
            else:
                print(f"❌ College dashboard failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ College dashboard error: {e}")
            return False
    
    def test_college_students(self):
        """Test students listing with college data"""
        print("👥 Testing College Students...")
        
        try:
            response = self.session.get(f"{self.base_url}/students")
            if response.status_code == 200:
                print("✅ College students page loaded successfully")
                return True
            else:
                print(f"❌ College students page failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ College students page error: {e}")
            return False
    
    def test_college_analytics(self):
        """Test analytics with college metrics"""
        print("📈 Testing College Analytics...")
        
        try:
            response = self.session.get(f"{self.base_url}/analytics")
            if response.status_code == 200:
                print("✅ College analytics loaded successfully")
                return True
            else:
                print(f"❌ College analytics failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ College analytics error: {e}")
            return False
    
    def test_college_prediction(self):
        """Test AI prediction for college students"""
        print("🤖 Testing College Risk Analysis...")
        
        try:
            response = self.session.get(f"{self.base_url}/predict")
            if response.status_code == 200:
                print("✅ College risk analysis loaded successfully")
                return True
            else:
                print(f"❌ College risk analysis failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ College risk analysis error: {e}")
            return False
    
    def test_college_student_detail(self):
        """Test college student detail page"""
        print("👤 Testing College Student Profile...")
        
        try:
            response = self.session.get(f"{self.base_url}/student/1")
            if response.status_code == 200:
                print("✅ College student profile loaded successfully")
                return True
            else:
                print(f"❌ College student profile failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ College student profile error: {e}")
            return False
    
    def run_college_tests(self):
        """Run all college-specific tests"""
        print("🎓 Starting College EduGuard System Tests...")
        print("=" * 60)
        
        tests = [
            self.test_college_dashboard,
            self.test_college_students,
            self.test_college_analytics,
            self.test_college_prediction,
            self.test_college_student_detail
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()
        
        print("=" * 60)
        print(f"📊 College Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL COLLEGE TESTS PASSED! System is ready for college use!")
        else:
            print("⚠️ Some college tests failed. Please check the system.")
        
        return passed == total

if __name__ == "__main__":
    tester = CollegeSystemTester()
    tester.run_college_tests()
