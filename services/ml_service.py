import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class RiskPredictionModel:
    def __init__(self, model_path='model/risk_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = [
            'attendance_rate', 
            'average_score', 
            'assignment_completion_rate',
            'quiz_average', 
            'lms_engagement_score'
        ]
        
        # ensure model directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Load model if exists
        self.load_model()

    def load_model(self):
        """Load the trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                data = joblib.load(self.model_path)
                self.model = data['model']
                self.scaler = data['scaler']
                logger.info(f"Model loaded from {self.model_path}")
            else:
                logger.warning("No trained model found. Please train the model first.")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")

    def train_model(self, synthetic_data_size=1000):
        """
        Train the model using synthetic data (since we don't have historical data yet).
        In a real scenario, this would query the database.
        """
        logger.info("Generating synthetic training data...")
        
        # Generate synthetic data
        np.random.seed(42)
        
        # Features
        # 1. Attendance Rate (0-100)
        attendance = np.random.normal(85, 15, synthetic_data_size)
        attendance = np.clip(attendance, 0, 100)
        
        # 2. Average Score (0-100)
        scores = np.random.normal(75, 15, synthetic_data_size)
        scores = np.clip(scores, 0, 100)
        
        # 3. Assignment Completion Rate (0-100)
        assignments = np.random.normal(80, 20, synthetic_data_size)
        assignments = np.clip(assignments, 0, 100)
        
        # 4. Quiz Average (0-100)
        quizzes = np.random.normal(70, 20, synthetic_data_size)
        quizzes = np.clip(quizzes, 0, 100)
        
        # 5. LMS Engagement Score (0-100)
        engagement = np.random.normal(60, 25, synthetic_data_size)
        engagement = np.clip(engagement, 0, 100)
        
        X = pd.DataFrame({
            'attendance_rate': attendance,
            'average_score': scores,
            'assignment_completion_rate': assignments,
            'quiz_average': quizzes,
            'lms_engagement_score': engagement
        })
        
        # Generate Target Variable: Dropout Risk (Low, Medium, High)
        # Logic for ground truth (to train the model):
        # - Low Attendance (<60) OR Low Scores (<50) -> High Risk
        # - Moderate Attendance (<75) OR Moderate Scores (<65) -> Medium Risk
        # - Else -> Low Risk
        
        y = []
        for i in range(synthetic_data_size):
             # Add some noise/randomness to make it realistic
            risk_score = (
                (100 - attendance[i]) * 0.4 +
                (100 - scores[i]) * 0.3 + 
                (100 - assignments[i]) * 0.1 +
                (100 - quizzes[i]) * 0.1 +
                (100 - engagement[i]) * 0.1
            ) + np.random.normal(0, 5) # Noise
            
            if risk_score > 50 or attendance[i] < 50:
                y.append('High')
            elif risk_score > 30:
                y.append('Medium')
            else:
                y.append('Low')
                
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scaling
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        logger.info("Training Random Forest Classifier...")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        
        logger.info(f"Model Training Completed. Accuracy: {accuracy:.2f}")
        logger.info(f"Classification Report:\n{report}")
        
        # Save model
        joblib.dump({'model': self.model, 'scaler': self.scaler}, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
        
        return {
            'success': True,
            'accuracy': accuracy,
            'model_path': self.model_path
        }

    def predict_risk(self, student_data):
        """
        Predict risk for a single student.
        
        Args:
            student_data (dict): Dictionary containing feature values:
                - attendance_rate
                - average_score
                - assignment_completion_rate
                - quiz_average
                - lms_engagement_score
        
        Returns:
            dict: {
                'risk_level': 'High'|'Medium'|'Low', 
                'probability': float (max probability of the predicted class),
                'risk_score': float (0-100 derived scale)
            }
        """
        if not self.model or not self.scaler:
            logger.error("Model not loaded. Attempting to load default...")
            self.load_model()
            if not self.model:
                 # If still no model, return default safe fallback
                return {'risk_level': 'Unknown', 'probability': 0.0, 'risk_score': 0.0}

        try:
            # Prepare input
            features = pd.DataFrame([student_data], columns=self.feature_names)
            features_scaled = self.scaler.transform(features)
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            max_prob = max(probabilities)
            
            # Calculate a continuous risk score (0-100) based on 'High' probability
            # We need to know which index corresponds to 'High'
            classes = self.model.classes_
            
            high_risk_idx = np.where(classes == 'High')[0]
            medium_risk_idx = np.where(classes == 'Medium')[0]
            
            high_prob = probabilities[high_risk_idx][0] if len(high_risk_idx) > 0 else 0
            medium_prob = probabilities[medium_risk_idx][0] if len(medium_risk_idx) > 0 else 0
            
            # Synthetic risk score calculation
            risk_score = (high_prob * 100) + (medium_prob * 50)
            
            return {
                'risk_level': prediction,
                'probability': float(max_prob),
                'risk_score': float(risk_score)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {'risk_level': 'Error', 'probability': 0.0, 'risk_score': 0.0}

# Singleton instance
ml_service = RiskPredictionModel()
