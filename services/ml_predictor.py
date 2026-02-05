"""
Machine Learning Dropout Prediction for EduGuard System
Uses scikit-learn for logistic regression prediction
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os
from datetime import datetime

class DropoutPredictor:
    """Machine Learning model for dropout prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = 'models/dropout_model.pkl'
        self.scaler_path = 'models/scaler.pkl'
        
    def prepare_data(self):
        """Prepare training data from database"""
        from models import Student, Attendance, AcademicRecord, RiskProfile, db
        
        try:
            # Get all students with their data
            students = db.session.query(
                Student, Attendance, AcademicRecord, RiskProfile
            ).join(
                Attendance, Student.id == Attendance.student_id
            ).join(
                AcademicRecord, Student.id == AcademicRecord.student_id
            ).outerjoin(
                RiskProfile, Student.id == RiskProfile.student_id
            ).all()
            
            data = []
            labels = []
            
            for student in students:
                # Calculate features
                attendance_records = [a for a in student.attendance_records if a.status == 'Present']
                attendance_rate = len(attendance_records) / len(student.attendance_records) * 100 if student.attendance_records else 0
                
                academic_records = student.academic_records
                avg_score = np.mean([ar.calculate_grade_points() * 25 for ar in academic_records]) if academic_records else 0
                
                # Count failing courses
                failing_courses = len([ar for ar in academic_records if ar.calculate_grade_points() < 2.0])
                
                # Intervention count
                intervention_count = len(student.interventions)
                
                # Risk profile data
                risk_score = student.risk_profile.risk_score if student.risk_profile else 0
                
                # Features for ML model
                features = [
                    attendance_rate,  # Attendance percentage
                    avg_score,        # Average academic performance
                    failing_courses,   # Number of failing courses
                    intervention_count, # Number of interventions
                    risk_score,        # Current risk score
                    student.year or 1,  # Academic year
                    student.semester or 1, # Current semester
                    student.credits_completed or 0  # Credits completed
                ]
                
                data.append(features)
                
                # Label: 1 if high risk, 0 otherwise
                label = 1 if (student.risk_profile and student.risk_profile.risk_level in ['High', 'Critical']) else 0
                labels.append(label)
            
            return np.array(data), np.array(labels)
            
        except Exception as e:
            print(f"Error preparing data: {e}")
            return np.array([]), np.array([])
    
    def train_model(self):
        """Train the logistic regression model"""
        try:
            # Prepare data
            X, y = self.prepare_data()
            
            if len(X) == 0:
                print("No data available for training")
                return False
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = LogisticRegression(random_state=42, max_iter=1000)
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"Model trained successfully!")
            print(f"Accuracy: {accuracy:.4f}")
            print(f"Classification Report:\n{classification_report(y_test, y_pred)}")
            
            # Save model and scaler
            self.save_model()
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict_dropout_risk(self, student_id):
        """Predict dropout risk for a specific student"""
        try:
            from models import Student, Attendance, AcademicRecord, db
            
            # Get student data
            student = Student.query.get(student_id)
            if not student:
                return {'error': 'Student not found'}
            
            # Calculate features
            attendance_records = [a for a in student.attendance_records if a.status == 'Present']
            attendance_rate = len(attendance_records) / len(student.attendance_records) * 100 if student.attendance_records else 0
            
            academic_records = student.academic_records
            avg_score = np.mean([ar.calculate_grade_points() * 25 for ar in academic_records]) if academic_records else 0
            
            failing_courses = len([ar for ar in academic_records if ar.calculate_grade_points() < 2.0])
            intervention_count = len(student.interventions)
            
            risk_score = student.risk_profile.risk_score if student.risk_profile else 0
            
            # Prepare features for prediction
            features = np.array([[
                attendance_rate,
                avg_score,
                failing_courses,
                intervention_count,
                risk_score,
                student.year or 1,
                student.semester or 1,
                student.credits_completed or 0
            ]])
            
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Make prediction
            dropout_probability = self.model.predict_proba(features_scaled)[0][1]  # Probability of class 1 (dropout risk)
            prediction = self.model.predict(features_scaled)[0]
            
            # Determine risk level
            if dropout_probability > 0.8:
                risk_level = 'Critical'
            elif dropout_probability > 0.6:
                risk_level = 'High'
            elif dropout_probability > 0.3:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            return {
                'student_id': student_id,
                'dropout_probability': round(dropout_probability * 100, 2),
                'prediction': int(prediction),
                'risk_level': risk_level,
                'features': {
                    'attendance_rate': round(attendance_rate, 2),
                    'average_score': round(avg_score, 2),
                    'failing_courses': failing_courses,
                    'intervention_count': intervention_count,
                    'current_risk_score': risk_score
                },
                'model_confidence': max(self.model.predict_proba(features_scaled)[0]) * 100,
                'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}
    
    def save_model(self):
        """Save the trained model and scaler"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs('models', exist_ok=True)
            
            # Save model
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            # Save scaler
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            print(f"Model saved to {self.model_path}")
            print(f"Scaler saved to {self.scaler_path}")
            
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self):
        """Load the trained model and scaler"""
        try:
            # Load model
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"Model loaded from {self.model_path}")
            
            # Load scaler
            if os.path.exists(self.scaler_path):
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print(f"Scaler loaded from {self.scaler_path}")
            
            return self.model is not None
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def get_feature_importance(self):
        """Get feature importance from the model"""
        if self.model is None:
            return None
        
        try:
            feature_names = [
                'Attendance Rate',
                'Average Score',
                'Failing Courses',
                'Intervention Count',
                'Risk Score',
                'Academic Year',
                'Semester',
                'Credits Completed'
            ]
            
            importance = self.model.coef_[0] if hasattr(self.model, 'coef_') else [0] * len(feature_names)
            
            feature_importance = []
            for i, (name, imp) in enumerate(zip(feature_names, importance)):
                feature_importance.append({
                    'feature': name,
                    'importance': abs(imp),
                    'impact': 'Positive' if imp > 0 else 'Negative'
                })
            
            # Sort by importance
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            return feature_importance
            
        except Exception as e:
            print(f"Error getting feature importance: {e}")
            return None
    
    def batch_predict_students(self, student_ids):
        """Batch predict for multiple students"""
        results = []
        
        for student_id in student_ids:
            result = self.predict_dropout_risk(student_id)
            results.append(result)
        
        return results

# Global predictor instance
predictor = DropoutPredictor()

def train_dropout_model():
    """Train the dropout prediction model"""
    print("🤖 Training Dropout Prediction Model...")
    success = predictor.train_model()
    
    if success:
        print("✅ Model training completed successfully!")
        return True
    else:
        print("❌ Model training failed!")
        return False

def predict_student_dropout(student_id):
    """Predict dropout risk for a student"""
    # Load model if not already loaded
    if predictor.model is None:
        predictor.load_model()
    
    return predictor.predict_dropout_risk(student_id)

def get_model_statistics():
    """Get model performance statistics"""
    if predictor.model is None:
        return None
    
    feature_importance = predictor.get_feature_importance()
    
    return {
        'model_loaded': predictor.model is not None,
        'feature_importance': feature_importance,
        'last_trained': datetime.fromtimestamp(os.path.getmtime(predictor.model_path)).strftime('%Y-%m-%d %H:%M') if os.path.exists(predictor.model_path) else None
    }
