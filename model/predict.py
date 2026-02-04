"""
CLI-based Student Dropout Prediction System
Early Warning System for Reducing Student Dropout Rates - NEP 2020 Aligned
"""

import sys
import os
import joblib
import numpy as np
from datetime import datetime

class DropoutPredictorCLI:
    """
    Command Line Interface for Student Dropout Prediction
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = None
        self.load_model_components()
    
    def load_model_components(self):
        """
        Load trained model, scaler, and feature names
        """
        try:
            # Load model
            self.model = joblib.load('model/model.pkl')
            
            # Load scaler
            self.scaler = joblib.load('model/scaler.pkl')
            
            # Load feature names
            self.features = joblib.load('model/features.pkl')
            
            print("✅ Model components loaded successfully!")
            
        except FileNotFoundError as e:
            print(f"❌ Error: Model files not found. Please run train_model.py first.")
            print(f"   Missing file: {e}")
            sys.exit(1)
    
    def get_user_input(self):
        """
        Get student data from user input
        """
        print("\n" + "="*60)
        print("🎓 STUDENT DROPOUT RISK ASSESSMENT")
        print("="*60)
        print("Please enter the following student information:")
        print("-" * 60)
        
        try:
            # Get attendance
            while True:
                attendance = input("📊 Attendance Percentage (0-100): ").strip()
                try:
                    attendance = float(attendance)
                    if 0 <= attendance <= 100:
                        break
                    else:
                        print("⚠️  Please enter a value between 0 and 100")
                except ValueError:
                    print("⚠️  Please enter a valid number")
            
            # Get marks
            while True:
                marks = input("📚 Academic Marks (0-100): ").strip()
                try:
                    marks = float(marks)
                    if 0 <= marks <= 100:
                        break
                    else:
                        print("⚠️  Please enter a value between 0 and 100")
                except ValueError:
                    print("⚠️  Please enter a valid number")
            
            # Get behavior score
            while True:
                behavior = input("🤝 Behavior Score (1-10, where 10 = Excellent): ").strip()
                try:
                    behavior = float(behavior)
                    if 1 <= behavior <= 10:
                        break
                    else:
                        print("⚠️  Please enter a value between 1 and 10")
                except ValueError:
                    print("⚠️  Please enter a valid number")
            
            return attendance, marks, behavior
            
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user.")
            sys.exit(0)
    
    def calculate_risk_score(self, attendance, marks, behavior_score):
        """
        Calculate comprehensive risk score
        """
        # Risk factors (higher values indicate higher risk)
        attendance_risk = (100 - attendance) * 0.4
        academic_risk = (100 - marks) * 0.4
        behavior_risk = (10 - behavior_score) * 2
        
        total_risk = attendance_risk + academic_risk + behavior_risk
        return round(total_risk, 2)
    
    def predict_dropout_risk(self, attendance, marks, behavior_score):
        """
        Predict dropout risk using trained model
        """
        # Calculate risk score
        risk_score = self.calculate_risk_score(attendance, marks, behavior_score)
        
        # Prepare features
        features = np.array([[attendance, marks, behavior_score, risk_score]])
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0]
        
        return {
            'prediction': int(prediction),
            'risk_level': 'HIGH RISK' if prediction == 1 else 'SAFE',
            'probability': {
                'safe': float(probability[0]),
                'at_risk': float(probability[1])
            },
            'risk_score': risk_score,
            'confidence': max(probability) * 100
        }
    
    def display_results(self, results, attendance, marks, behavior_score):
        """
        Display prediction results with detailed analysis
        """
        print("\n" + "="*60)
        print("📋 PREDICTION RESULTS")
        print("="*60)
        
        # Input summary
        print(f"📊 Attendance: {attendance}%")
        print(f"📚 Academic Marks: {marks}%")
        print(f"🤝 Behavior Score: {behavior_score}/10")
        print(f"📈 Calculated Risk Score: {results['risk_score']}")
        print("-" * 60)
        
        # Main prediction
        risk_level = results['risk_level']
        if risk_level == 'HIGH RISK':
            print("🚨 PREDICTION: HIGH RISK OF DROPOUT")
            print("⚠️  Immediate intervention recommended!")
        else:
            print("✅ PREDICTION: SAFE")
            print("🎉 Low risk of dropout - Continue monitoring!")
        
        # Probability breakdown
        print("\n📊 Probability Analysis:")
        print(f"   Probability of being SAFE: {results['probability']['safe']*100:.2f}%")
        print(f"   Probability of being AT-RISK: {results['probability']['at_risk']*100:.2f}%")
        print(f"   Model Confidence: {results['confidence']:.2f}%")
        
        # Risk assessment
        print("\n🎯 Risk Assessment:")
        if results['risk_score'] < 20:
            print("   🟢 Very Low Risk: Student is performing well")
        elif results['risk_score'] < 40:
            print("   🟡 Low Risk: Monitor regularly")
        elif results['risk_score'] < 60:
            print("   🟠 Medium Risk: Consider counseling")
        else:
            print("   🔴 High Risk: Immediate attention required")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if risk_level == 'HIGH RISK':
            print("   • Schedule immediate counseling session")
            print("   • Analyze specific areas of concern")
            print("   • Develop personalized improvement plan")
            print("   • Increase monitoring frequency")
            print("   • Involve parents/guardians if applicable")
        else:
            print("   • Continue regular monitoring")
            print("   • Maintain current performance levels")
            print("   • Provide encouragement and support")
        
        print("="*60)
    
    def batch_prediction(self, student_data):
        """
        Perform batch prediction for multiple students
        """
        print("\n" + "="*60)
        print("📊 BATCH PREDICTION RESULTS")
        print("="*60)
        
        results = []
        for i, student in enumerate(student_data, 1):
            attendance, marks, behavior = student
            result = self.predict_dropout_risk(attendance, marks, behavior)
            results.append(result)
            
            print(f"\nStudent {i}:")
            print(f"  Attendance: {attendance}%, Marks: {marks}%, Behavior: {behavior}")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Risk Score: {result['risk_score']}")
            print(f"  Confidence: {result['confidence']:.2f}%")
        
        # Summary statistics
        at_risk_count = sum(1 for r in results if r['risk_level'] == 'HIGH RISK')
        total_students = len(results)
        
        print(f"\n📈 SUMMARY:")
        print(f"  Total Students: {total_students}")
        print(f"  At-Risk Students: {at_risk_count} ({at_risk_count/total_students*100:.1f}%)")
        print(f"  Safe Students: {total_students - at_risk_count} ({(total_students-at_risk_count)/total_students*100:.1f}%)")
        
        return results
    
    def interactive_mode(self):
        """
        Interactive prediction mode
        """
        while True:
            try:
                # Get user input
                attendance, marks, behavior = self.get_user_input()
                
                # Make prediction
                results = self.predict_dropout_risk(attendance, marks, behavior)
                
                # Display results
                self.display_results(results, attendance, marks, behavior)
                
                # Ask for another prediction
                print("\n" + "-"*60)
                choice = input("Would you like to assess another student? (y/n): ").strip().lower()
                if choice not in ['y', 'yes']:
                    print("\n👋 Thank you for using the Student Dropout Prediction System!")
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Operation cancelled by user.")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again.")
    
    def demo_mode(self):
        """
        Demo mode with sample predictions
        """
        print("\n" + "="*60)
        print("🎬 DEMO MODE - SAMPLE PREDICTIONS")
        print("="*60)
        
        # Sample student data
        sample_students = [
            (95, 88, 9),   # High performer
            (75, 65, 6),   # Average performer
            (60, 45, 4),   # At-risk student
            (85, 72, 7),   # Good performer
            (70, 55, 5),   # Medium risk
        ]
        
        student_names = ["High Performer", "Average Student", "At-Risk Student", "Good Student", "Medium Risk Student"]
        
        for i, (attendance, marks, behavior) in enumerate(sample_students):
            print(f"\n📊 {student_names[i]}:")
            print(f"   Attendance: {attendance}%, Marks: {marks}%, Behavior: {behavior}/10")
            
            result = self.predict_dropout_risk(attendance, marks, behavior)
            print(f"   🎯 Prediction: {result['risk_level']}")
            print(f"   📈 Risk Score: {result['risk_score']}")
            print(f"   🔍 Confidence: {result['confidence']:.2f}%")

def main():
    """
    Main function for CLI interface
    """
    print("🎓 AI-DRIVEN STUDENT DROPOUT PREDICTION SYSTEM")
    print("=" * 60)
    print("Early Warning System for Reducing Student Dropout Rates")
    print("Aligned with NEP 2020 Objectives")
    print("=" * 60)
    
    # Initialize predictor
    predictor = DropoutPredictorCLI()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'demo':
            predictor.demo_mode()
        elif mode == 'batch':
            # Example batch mode
            sample_data = [
                (85, 75, 7),
                (65, 55, 5),
                (90, 82, 8),
            ]
            predictor.batch_prediction(sample_data)
        else:
            print("Usage:")
            print("  python predict.py        - Interactive mode")
            print("  python predict.py demo    - Demo mode")
            print("  python predict.py batch   - Batch mode")
    else:
        # Interactive mode
        predictor.interactive_mode()

if __name__ == "__main__":
    main()
