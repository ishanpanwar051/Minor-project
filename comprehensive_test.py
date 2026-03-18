"""
Comprehensive System Test and Enhancement Script
Tests all components and creates sample data for ML training
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Student, Attendance, RiskProfile, Alert
from datetime import datetime, date, timedelta
import random

def create_comprehensive_sample_data():
    """Create comprehensive sample data for testing and ML training"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Creating comprehensive sample data...")
        
        # Create diverse student profiles
        departments = ['Computer Science', 'Engineering', 'Business', 'Arts', 'Science', 'Medicine']
        
        # Create 50 students with diverse profiles
        for i in range(50):
            student_id = f'ST{i+1:03d}'
            
            # Check if student already exists
            if Student.query.filter_by(student_id=student_id).first():
                continue
            
            # Generate realistic student data
            first_name = f'FirstName{i+1}'
            last_name = f'LastName{i+1}'
            email = f'{first_name.lower()}.{last_name.lower()}@eduguard.edu'
            department = random.choice(departments)
            year = random.randint(1, 4)
            semester = random.randint(1, 2)
            
            # Academic performance (correlated with year)
            base_gpa = random.uniform(5.0, 9.5)
            gpa = max(2.0, base_gpa - (year - 1) * 0.5)  # GPA tends to decrease over years
            academic_performance = gpa * 10  # Convert to 0-100 scale
            
            # Credits completed (realistic progression)
            credits_completed = (year - 1) * 30 + random.randint(10, 25)
            
            # Create user account
            user = User(
                username=student_id.lower(),
                email=email,
                role='student'
            )
            user.set_password('student123')
            db.session.add(user)
            db.session.flush()
            
            # Create student profile
            student = Student(
                user_id=user.id,
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department,
                year=year,
                semester=semester,
                gpa=gpa,
                enrollment_date=date(2022 - year + 1, 9, 1),
                credits_completed=credits_completed,
                parent_name=f'Parent of {first_name}',
                parent_email=f'parent.{first_name.lower()}@example.com',
                parent_phone=f'555-{i+1:04d}'
            )
            db.session.add(student)
            db.session.flush()
            
            # Create realistic risk factors (correlated with academic performance)
            financial_issues = random.random() < 0.4 if academic_performance < 60 else random.random() < 0.15
            family_problems = random.random() < 0.35 if academic_performance < 65 else random.random() < 0.1
            health_issues = random.random() < 0.25
            social_isolation = random.random() < 0.2 if academic_performance < 70 else random.random() < 0.08
            
            # Mental wellbeing (correlated with other factors)
            mental_wellbeing = random.uniform(3, 10)
            if financial_issues:
                mental_wellbeing = max(3, mental_wellbeing - 2)
            if family_problems:
                mental_wellbeing = max(3, mental_wellbeing - 1.5)
            if social_isolation:
                mental_wellbeing = max(3, mental_wellbeing - 1)
            
            # Attendance (correlated with performance and wellbeing)
            base_attendance = random.uniform(70, 95)
            if mental_wellbeing < 5:
                base_attendance -= 10
            if financial_issues:
                base_attendance -= 5
            attendance_rate = max(60, min(95, base_attendance))
            
            # Create risk profile
            risk_profile = RiskProfile(
                student_id=student.id,
                attendance_rate=attendance_rate,
                academic_performance=academic_performance,
                financial_issues=financial_issues,
                family_problems=family_problems,
                health_issues=health_issues,
                social_isolation=social_isolation,
                mental_wellbeing_score=round(mental_wellbeing, 1)
            )
            
            # Calculate risk score
            risk_profile.update_risk_score(use_ml=False)
            db.session.add(risk_profile)
            db.session.flush()
            
            # Create attendance records for the last 60 days
            for days_ago in range(60):
                attendance_date = date.today() - timedelta(days=days_ago)
                
                # Attendance probability based on student's attendance rate
                attendance_prob = attendance_rate / 100
                
                # Add some randomness
                if random.random() < attendance_prob:
                    status = random.choice(['Present', 'Present', 'Present', 'Late'])  # 75% Present, 25% Late
                else:
                    status = random.choice(['Absent', 'Absent', 'Excused'])  # 66% Absent, 33% Excused
                
                attendance = Attendance(
                    student_id=student.id,
                    date=attendance_date,
                    status=status,
                    course=f'{department[:3].upper()}{random.randint(100, 999)}'
                )
                db.session.add(attendance)
            
            # Create alerts for high-risk students
            if risk_profile.risk_level in ['High', 'Critical']:
                alert = Alert(
                    student_id=student.id,
                    alert_type='Risk Level Change',
                    severity=risk_profile.risk_level,
                    title=f'{risk_profile.risk_level} Risk Student: {first_name} {last_name}',
                    description=f'Student shows {risk_profile.risk_level.lower()} risk factors: {risk_profile.risk_reasons}',
                    status='Active'
                )
                db.session.add(alert)
            
            if (i + 1) % 10 == 0:
                print(f"✅ Created {i + 1} students...")
        
        db.session.commit()
        print(f"✅ Successfully created comprehensive sample data!")
        
        # Print statistics
        total_students = Student.query.count()
        risk_stats = {
            'low': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Low').count(),
            'medium': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Medium').count(),
            'high': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'High').count(),
            'critical': Student.query.join(RiskProfile).filter(RiskProfile.risk_level == 'Critical').count()
        }
        
        print(f"\n📊 Database Statistics:")
        print(f"Total Students: {total_students}")
        print(f"Risk Distribution:")
        print(f"  Low Risk: {risk_stats['low']}")
        print(f"  Medium Risk: {risk_stats['medium']}")
        print(f"  High Risk: {risk_stats['high']}")
        print(f"  Critical Risk: {risk_stats['critical']}")
        
        return True

def test_ml_training():
    """Test ML model training with the new data"""
    print("\n🤖 Testing ML Model Training...")
    
    try:
        from train_ml_model import train_and_save_model, update_existing_risk_profiles
        
        # Train the model
        if train_and_save_model():
            print("✅ ML Model training successful!")
            
            # Update existing profiles
            if update_existing_risk_profiles():
                print("✅ Risk profiles updated with ML predictions!")
                return True
            else:
                print("⚠️ Risk profile update failed")
                return False
        else:
            print("❌ ML Model training failed")
            return False
            
    except Exception as e:
        print(f"❌ ML Training Error: {e}")
        return False

def test_system_components():
    """Test all system components"""
    print("\n🧪 Testing System Components...")
    
    app = create_app()
    
    with app.app_context():
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Database Connection
        total_tests += 1
        try:
            db.session.execute('SELECT 1')
            print("✅ Database connection successful")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
        
        # Test 2: Student Data
        total_tests += 1
        try:
            students = Student.query.limit(5).all()
            print(f"✅ Student data access successful ({len(students)} students found)")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Student data access failed: {e}")
        
        # Test 3: Risk Profile Calculation
        total_tests += 1
        try:
            student = Student.query.first()
            if student and student.risk_profile:
                original_score = student.risk_profile.risk_score
                student.risk_profile.update_risk_score(use_ml=False)
                new_score = student.risk_profile.risk_score
                print(f"✅ Risk profile calculation successful (score: {new_score})")
                tests_passed += 1
            else:
                print("⚠️ No student with risk profile found")
        except Exception as e:
            print(f"❌ Risk profile calculation failed: {e}")
        
        # Test 4: Alert System
        total_tests += 1
        try:
            alerts = Alert.query.limit(5).all()
            print(f"✅ Alert system working ({len(alerts)} alerts found)")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Alert system failed: {e}")
        
        # Test 5: ML Predictor
        total_tests += 1
        try:
            from enhanced_ai_predictor import risk_predictor
            student_data = {
                'gpa': 7.5,
                'attendance_rate': 85,
                'academic_performance': 75,
                'credits_completed': 60,
                'year': 2,
                'semester': 1,
                'financial_issues': False,
                'family_problems': False,
                'health_issues': False,
                'social_isolation': False,
                'mental_wellbeing_score': 8.0
            }
            prediction = risk_predictor.predict_risk(student_data)
            print(f"✅ ML Predictor working (risk: {prediction['risk_level']})")
            tests_passed += 1
        except Exception as e:
            print(f"❌ ML Predictor failed: {e}")
        
        print(f"\n📋 Test Results: {tests_passed}/{total_tests} tests passed")
        return tests_passed == total_tests

def main():
    """Main testing and enhancement function"""
    print("🚀 EduGuard Comprehensive System Test & Enhancement")
    print("=" * 60)
    
    # Step 1: Create comprehensive sample data
    if create_comprehensive_sample_data():
        print("✅ Sample data creation successful!")
    else:
        print("❌ Sample data creation failed!")
        return
    
    # Step 2: Test system components
    if test_system_components():
        print("✅ System components test passed!")
    else:
        print("⚠️ Some system components have issues")
    
    # Step 3: Test ML training
    if test_ml_training():
        print("✅ ML system test passed!")
    else:
        print("⚠️ ML system needs attention")
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive system test completed!")
    print("🌐 You can now access the enhanced dashboard at: http://127.0.0.1:5000")
    print("🔐 Login with: admin@eduguard.edu / admin123")

if __name__ == '__main__':
    main()
