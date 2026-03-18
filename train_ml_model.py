"""
ML Model Training Script for EduGuard
Trains the enhanced risk prediction model with existing student data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Student, RiskProfile, Attendance
from enhanced_ai_predictor import EnhancedRiskPredictor
import pandas as pd
from datetime import datetime, date, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_training_data():
    """Prepare training data from existing student records"""
    app = create_app()
    
    with app.app_context():
        # Get all students with their data
        students = Student.query.all()
        
        if len(students) < 5:
            logger.warning("Not enough student data for training. Creating synthetic data...")
            return create_synthetic_training_data()
        
        training_data = []
        
        for student in students:
            # Get attendance data
            attendance_records = Attendance.query.filter_by(student_id=student.id).all()
            
            # Calculate attendance rate
            if attendance_records:
                attendance_rate = (len([a for a in attendance_records if a.status == 'Present']) / len(attendance_records)) * 100
            else:
                attendance_rate = 85.0  # Default assumption
            
            # Get risk profile
            risk_profile = student.risk_profile
            
            # Prepare student data
            student_data = {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'gpa': student.gpa or 3.0,
                'attendance_rate': attendance_rate,
                'academic_performance': risk_profile.academic_performance if risk_profile else 75.0,
                'credits_completed': student.credits_completed or 30,
                'year': student.year or 1,
                'semester': student.semester or 1,
                'financial_issues': risk_profile.financial_issues if risk_profile else False,
                'family_problems': risk_profile.family_problems if risk_profile else False,
                'health_issues': risk_profile.health_issues if risk_profile else False,
                'social_isolation': risk_profile.social_isolation if risk_profile else False,
                'mental_wellbeing_score': risk_profile.mental_wellbeing_score if risk_profile else 8.0,
                'existing_risk_level': risk_profile.risk_level if risk_profile else 'Low'
            }
            
            training_data.append(student_data)
        
        return pd.DataFrame(training_data)

def create_synthetic_training_data():
    """Create synthetic training data when real data is insufficient"""
    logger.info("Creating synthetic training data...")
    
    import random
    
    synthetic_data = []
    
    # Create diverse student profiles
    for i in range(50):
        # Generate realistic student data
        gpa = round(random.uniform(2.0, 9.0), 1)
        attendance_rate = round(random.uniform(60, 95), 1)
        academic_performance = round(random.uniform(30, 90), 1)
        
        # Personal factors (correlated with academic performance)
        financial_issues = random.random() < 0.3 if academic_performance < 60 else random.random() < 0.1
        family_problems = random.random() < 0.25 if academic_performance < 65 else random.random() < 0.05
        health_issues = random.random() < 0.2
        social_isolation = random.random() < 0.15 if attendance_rate < 75 else random.random() < 0.05
        
        # Mental wellbeing (correlated with other factors)
        mental_wellbeing = random.uniform(3, 10)
        if financial_issues or family_problems:
            mental_wellbeing = max(3, mental_wellbeing - 2)
        if social_isolation:
            mental_wellbeing = max(3, mental_wellbeing - 1)
        
        student_data = {
            'student_id': f'ST{i+1:03d}',
            'first_name': f'Student{i+1}',
            'last_name': f'Name{i+1}',
            'gpa': gpa,
            'attendance_rate': attendance_rate,
            'academic_performance': academic_performance,
            'credits_completed': random.randint(15, 120),
            'year': random.randint(1, 4),
            'semester': random.randint(1, 2),
            'financial_issues': financial_issues,
            'family_problems': family_problems,
            'health_issues': health_issues,
            'social_isolation': social_isolation,
            'mental_wellbeing_score': round(mental_wellbeing, 1),
            'existing_risk_level': 'Low'  # Will be recalculated
        }
        
        synthetic_data.append(student_data)
    
    return pd.DataFrame(synthetic_data)

def train_and_save_model():
    """Train the ML model and save it"""
    logger.info("Starting ML model training...")
    
    # Initialize predictor
    predictor = EnhancedRiskPredictor()
    
    # Get training data
    training_df = prepare_training_data()
    logger.info(f"Prepared {len(training_df)} training samples")
    
    # Generate training data with labels
    training_data = predictor.generate_training_data(training_df)
    logger.info(f"Generated {len(training_data)} labeled training samples")
    
    # Train models
    success = predictor.train_models(training_data)
    
    if success:
        # Save the trained model
        model_path = os.path.join(os.path.dirname(__file__), 'ml_models', 'risk_predictor.joblib')
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        predictor.save_model(model_path)
        logger.info(f"Model saved successfully to {model_path}")
        
        # Test the model with a sample
        test_student = training_data.iloc[0].to_dict()
        prediction = predictor.predict_risk(test_student)
        logger.info(f"Sample prediction: {prediction}")
        
        return True
    else:
        logger.error("Model training failed")
        return False

def update_existing_risk_profiles():
    """Update existing student risk profiles with ML predictions"""
    app = create_app()
    
    with app.app_context():
        # Load trained model
        predictor = EnhancedRiskPredictor()
        model_path = os.path.join(os.path.dirname(__file__), 'ml_models', 'risk_predictor.joblib')
        
        if not predictor.load_model(model_path):
            logger.warning("Could not load trained model. Skipping profile updates.")
            return False
        
        # Update all student risk profiles
        students = Student.query.all()
        updated_count = 0
        
        for student in students:
            try:
                # Get current data
                attendance_records = Attendance.query.filter_by(student_id=student.id).all()
                attendance_rate = (len([a for a in attendance_records if a.status == 'Present']) / len(attendance_records)) * 100 if attendance_records else 85.0
                
                student_data = {
                    'gpa': student.gpa or 3.0,
                    'attendance_rate': attendance_rate,
                    'academic_performance': student.risk_profile.academic_performance if student.risk_profile else 75.0,
                    'credits_completed': student.credits_completed or 30,
                    'year': student.year or 1,
                    'semester': student.semester or 1,
                    'financial_issues': student.risk_profile.financial_issues if student.risk_profile else False,
                    'family_problems': student.risk_profile.family_problems if student.risk_profile else False,
                    'health_issues': student.risk_profile.health_issues if student.risk_profile else False,
                    'social_isolation': student.risk_profile.social_isolation if student.risk_profile else False,
                    'mental_wellbeing_score': student.risk_profile.mental_wellbeing_score if student.risk_profile else 8.0
                }
                
                # Get ML prediction
                prediction = predictor.predict_risk(student_data)
                
                # Update risk profile
                if student.risk_profile:
                    student.risk_profile.ml_prediction = prediction['risk_score']
                    student.risk_profile.ml_confidence = prediction['confidence']
                    student.risk_profile.ml_features = str(prediction['ml_features'])
                    student.risk_profile.update_risk_score(use_ml=True)
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating student {student.student_id}: {e}")
        
        db.session.commit()
        logger.info(f"Updated {updated_count} student risk profiles with ML predictions")
        return True

if __name__ == '__main__':
    logger.info("EduGuard ML Model Training")
    logger.info("=" * 50)
    
    # Train the model
    if train_and_save_model():
        logger.info("✅ Model training completed successfully!")
        
        # Update existing profiles
        if update_existing_risk_profiles():
            logger.info("✅ Risk profiles updated successfully!")
        else:
            logger.warning("⚠️ Risk profile update failed")
    else:
        logger.error("❌ Model training failed")
    
    logger.info("=" * 50)
    logger.info("Training process completed")
