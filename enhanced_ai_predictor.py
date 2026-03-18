"""
Enhanced AI Risk Prediction System for EduGuard
Combines rule-based and machine learning approaches for accurate dropout risk prediction
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRiskPredictor:
    """Enhanced AI system for student dropout risk prediction"""
    
    def __init__(self):
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.is_trained = False
        
    def prepare_features(self, student_data):
        """
        Prepare comprehensive features for ML prediction
        
        Features include:
        - Academic metrics (GPA, attendance rate, credits completed)
        - Personal factors (financial, family, health, social)
        - Mental wellbeing score
        - Temporal features (year, semester)
        - Risk indicators (binary flags)
        """
        features = {}
        
        # Academic Features
        features['gpa'] = float(student_data.get('gpa', 0))
        features['attendance_rate'] = float(student_data.get('attendance_rate', 0))
        features['academic_performance'] = float(student_data.get('academic_performance', 0))
        features['credits_completed'] = int(student_data.get('credits_completed', 0))
        features['year'] = int(student_data.get('year', 1))
        features['semester'] = int(student_data.get('semester', 1))
        
        # Personal Risk Factors (binary)
        features['financial_issues'] = 1 if student_data.get('financial_issues', False) else 0
        features['family_problems'] = 1 if student_data.get('family_problems', False) else 0
        features['health_issues'] = 1 if student_data.get('health_issues', False) else 0
        features['social_isolation'] = 1 if student_data.get('social_isolation', False) else 0
        
        # Mental Wellbeing (normalized)
        features['mental_wellbeing_score'] = float(student_data.get('mental_wellbeing_score', 10)) / 10.0
        
        # Risk Count Features
        personal_risk_count = (
            features['financial_issues'] + 
            features['family_problems'] + 
            features['health_issues'] + 
            features['social_isolation']
        )
        features['personal_risk_count'] = personal_risk_count
        
        # Academic Risk Indicators
        features['low_attendance_flag'] = 1 if features['attendance_rate'] < 75 else 0
        features['very_low_attendance_flag'] = 1 if features['attendance_rate'] < 60 else 0
        features['poor_academic_flag'] = 1 if features['academic_performance'] < 40 else 0
        features['critical_academic_flag'] = 1 if features['academic_performance'] < 30 else 0
        
        # Combined Risk Features
        features['academic_risk_score'] = max(0, 100 - features['academic_performance']) / 100.0
        features['attendance_risk_score'] = max(0, 100 - features['attendance_rate']) / 100.0
        
        # Mental Health Risk
        features['mental_health_risk'] = 1 if features['mental_wellbeing_score'] < 0.4 else 0
        
        return features
    
    def generate_training_data(self, students_df):
        """
        Generate training data with labels based on historical patterns
        Uses rule-based approach to create initial labels for supervised learning
        """
        training_data = []
        
        for _, student in students_df.iterrows():
            features = self.prepare_features(student.to_dict())
            
            # Generate risk label based on comprehensive assessment
            risk_score = 0
            
            # Academic risks (40% weight)
            if features['attendance_rate'] < 60:
                risk_score += 40
            elif features['attendance_rate'] < 75:
                risk_score += 20
                
            if features['academic_performance'] < 30:
                risk_score += 40
            elif features['academic_performance'] < 40:
                risk_score += 20
            
            # Personal risks (40% weight)
            personal_risks = (
                features['financial_issues'] * 10 +
                features['family_problems'] * 10 +
                features['health_issues'] * 10 +
                features['social_isolation'] * 5 +
                features['mental_health_risk'] * 5
            )
            risk_score += min(40, personal_risks)
            
            # Temporal risk (20% weight)
            if features['year'] > 2 and features['credits_completed'] < features['year'] * 30:
                risk_score += 10
            if features['semester'] > 1 and features['gpa'] < 2.0:
                risk_score += 10
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = 3  # Critical
            elif risk_score >= 50:
                risk_level = 2  # High
            elif risk_score >= 30:
                risk_level = 1  # Medium
            else:
                risk_level = 0  # Low
            
            features['risk_level'] = risk_level
            training_data.append(features)
        
        return pd.DataFrame(training_data)
    
    def train_models(self, training_data):
        """
        Train ensemble of ML models for risk prediction
        """
        if len(training_data) < 10:
            logger.warning("Insufficient training data. Using rule-based approach.")
            return False
        
        # Prepare features and target
        feature_cols = [col for col in training_data.columns if col != 'risk_level']
        self.feature_columns = feature_cols
        
        X = training_data[feature_cols]
        y = training_data['risk_level']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train models
        self.rf_model.fit(X_train, y_train)
        self.gb_model.fit(X_train, y_train)
        
        # Evaluate models
        rf_score = self.rf_model.score(X_test, y_test)
        gb_score = self.gb_model.score(X_test, y_test)
        
        logger.info(f"Random Forest Accuracy: {rf_score:.3f}")
        logger.info(f"Gradient Boosting Accuracy: {gb_score:.3f}")
        
        # Cross-validation
        rf_cv = cross_val_score(self.rf_model, X_scaled, y, cv=5).mean()
        gb_cv = cross_val_score(self.gb_model, X_scaled, y, cv=5).mean()
        
        logger.info(f"Random Forest CV Score: {rf_cv:.3f}")
        logger.info(f"Gradient Boosting CV Score: {gb_cv:.3f}")
        
        self.is_trained = True
        return True
    
    def predict_risk(self, student_data):
        """
        Predict dropout risk for a student using ensemble approach
        Returns risk level, confidence, and contributing factors
        """
        features = self.prepare_features(student_data)
        
        if not self.is_trained:
            # Fall back to rule-based prediction
            return self._rule_based_prediction(features)
        
        # Prepare features for ML
        feature_df = pd.DataFrame([features])
        feature_df = feature_df[self.feature_columns]  # Ensure correct column order
        features_scaled = self.scaler.transform(feature_df)
        
        # Get predictions from both models
        rf_pred = self.rf_model.predict_proba(features_scaled)[0]
        gb_pred = self.gb_model.predict_proba(features_scaled)[0]
        
        # Ensemble prediction (weighted average)
        ensemble_pred = (rf_pred * 0.6 + gb_pred * 0.4)
        
        # Determine risk level
        risk_level_idx = np.argmax(ensemble_pred)
        confidence = ensemble_pred[risk_level_idx]
        
        risk_levels = ['Low', 'Medium', 'High', 'Critical']
        predicted_risk = risk_levels[risk_level_idx]
        
        # Get feature importance
        feature_importance = self._get_feature_importance(features)
        
        return {
            'risk_level': predicted_risk,
            'risk_score': float(risk_level_idx * 25),
            'confidence': float(confidence),
            'rule_based_score': self._calculate_rule_based_score(features),
            'ml_features': features,
            'feature_importance': feature_importance,
            'prediction_method': 'ensemble_ml'
        }
    
    def _rule_based_prediction(self, features):
        """Fallback rule-based prediction"""
        score = self._calculate_rule_based_score(features)
        
        if score >= 70:
            risk_level = 'Critical'
        elif score >= 50:
            risk_level = 'High'
        elif score >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        confidence = min(1.0, score / 100.0 + 0.2)  # Basic confidence calculation
        
        return {
            'risk_level': risk_level,
            'risk_score': score,
            'confidence': confidence,
            'rule_based_score': score,
            'ml_features': features,
            'feature_importance': self._get_rule_based_importance(features),
            'prediction_method': 'rule_based'
        }
    
    def _calculate_rule_based_score(self, features):
        """Calculate traditional rule-based risk score"""
        score = 0
        
        # Academic factors (40%)
        if features['attendance_rate'] < 60:
            score += 40
        elif features['attendance_rate'] < 75:
            score += 20
            
        if features['academic_performance'] < 30:
            score += 40
        elif features['academic_performance'] < 40:
            score += 20
        
        # Personal factors (40%)
        if features['financial_issues']:
            score += 10
        if features['family_problems']:
            score += 10
        if features['health_issues']:
            score += 10
        if features['social_isolation']:
            score += 5
        if features['mental_health_risk']:
            score += 5
        
        # Temporal factors (20%)
        if features['year'] > 2 and features['credits_completed'] < features['year'] * 30:
            score += 10
        if features['semester'] > 1 and features['gpa'] < 2.0:
            score += 10
        
        return min(100, score)
    
    def _get_feature_importance(self, features):
        """Get feature importance from trained models"""
        if not self.is_trained:
            return self._get_rule_based_importance(features)
        
        # Get feature importance from Random Forest
        importance_dict = {}
        for i, feature in enumerate(self.feature_columns):
            importance_dict[feature] = float(self.rf_model.feature_importances_[i])
        
        # Sort by importance
        sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_importance[:5])  # Top 5 factors
    
    def _get_rule_based_importance(self, features):
        """Get rule-based feature importance"""
        importance = {}
        
        if features['attendance_rate'] < 75:
            importance['attendance_rate'] = 0.3
        if features['academic_performance'] < 40:
            importance['academic_performance'] = 0.25
        if features['financial_issues']:
            importance['financial_issues'] = 0.15
        if features['family_problems']:
            importance['family_problems'] = 0.15
        if features['health_issues']:
            importance['health_issues'] = 0.1
        if features['mental_health_risk']:
            importance['mental_health_risk'] = 0.05
        
        return importance
    
    def save_model(self, filepath):
        """Save trained models and scaler"""
        if self.is_trained:
            model_data = {
                'rf_model': self.rf_model,
                'gb_model': self.gb_model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, filepath)
            logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained models and scaler"""
        try:
            model_data = joblib.load(filepath)
            self.rf_model = model_data['rf_model']
            self.gb_model = model_data['gb_model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            self.is_trained = model_data['is_trained']
            logger.info(f"Model loaded from {filepath}")
            return True
        except FileNotFoundError:
            logger.warning(f"Model file not found: {filepath}")
            return False

# Global predictor instance
risk_predictor = EnhancedRiskPredictor()
