"""
AI-Driven Student Dropout Prediction Model
Early Warning System for Reducing Student Dropout Rates - NEP 2020 Aligned
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

class DropoutPredictionModel:
    """
    Machine Learning Model for Student Dropout Prediction
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.features = ['attendance', 'marks', 'behavior_score']
        self.target = 'dropout'
        
    def load_data(self, filepath):
        """
        Load and prepare dataset
        """
        print("Loading dataset...")
        self.data = pd.read_csv(filepath)
        print(f"Dataset loaded successfully with {len(self.data)} records")
        return self.data
    
    def explore_data(self):
        """
        Exploratory Data Analysis
        """
        print("\n" + "="*50)
        print("EXPLORATORY DATA ANALYSIS")
        print("="*50)
        
        # Basic statistics
        print("\nDataset Info:")
        print(self.data.info())
        
        print("\nDescriptive Statistics:")
        print(self.data.describe())
        
        # Dropout distribution
        print("\nDropout Distribution:")
        dropout_counts = self.data['dropout'].value_counts()
        print(dropout_counts)
        print(f"Dropout Rate: {dropout_counts[1]/len(self.data)*100:.2f}%")
        
        # Correlation analysis
        print("\nFeature Correlations:")
        correlations = self.data[self.features + [self.target]].corr()
        print(correlations[self.target].sort_values(ascending=False))
        
        return correlations
    
    def preprocess_data(self):
        """
        Data preprocessing and feature engineering
        """
        print("\n" + "="*50)
        print("DATA PREPROCESSING")
        print("="*50)
        
        # Check for missing values
        print("Missing Values:")
        print(self.data.isnull().sum())
        
        # Handle missing values (if any)
        self.data = self.data.dropna()
        
        # Feature engineering
        # Create risk score based on combined factors
        self.data['risk_score'] = (
            (100 - self.data['attendance']) * 0.4 +
            (100 - self.data['marks']) * 0.4 +
            (10 - self.data['behavior_score']) * 2
        )
        
        # Add risk_score to features
        self.features.append('risk_score')
        
        print(f"Features after engineering: {self.features}")
        print(f"Final dataset shape: {self.data.shape}")
        
        return self.data
    
    def split_data(self, test_size=0.2, random_state=42):
        """
        Split data into training and testing sets
        """
        print("\n" + "="*50)
        print("DATA SPLITTING")
        print("="*50)
        
        X = self.data[self.features]
        y = self.data[self.target]
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"Training set size: {X_train.shape[0]}")
        print(f"Testing set size: {X_test.shape[0]}")
        print(f"Features: {self.features}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_model(self, X_train, y_train):
        """
        Train Random Forest Classifier
        """
        print("\n" + "="*50)
        print("MODEL TRAINING")
        print("="*50)
        
        # Initialize Random Forest with optimized parameters
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        print("Random Forest Classifier trained successfully!")
        print(f"Model parameters: {self.model.get_params()}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        print(feature_importance)
        
        return self.model
    
    def evaluate_model(self, X_test, y_test):
        """
        Evaluate model performance
        """
        print("\n" + "="*50)
        print("MODEL EVALUATION")
        print("="*50)
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Safe', 'At-Risk']))
        
        # Confusion matrix
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        # Detailed metrics
        tn, fp, fn, tp = cm.ravel()
        sensitivity = tp / (tp + fn)  # True Positive Rate
        specificity = tn / (tn + fp)  # True Negative Rate
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        
        print(f"\nDetailed Metrics:")
        print(f"Sensitivity (Recall): {sensitivity:.4f}")
        print(f"Specificity: {specificity:.4f}")
        print(f"Precision: {precision:.4f}")
        
        return {
            'accuracy': accuracy,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'precision': precision,
            'confusion_matrix': cm,
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }
    
    def save_model(self, model_path='model/model.pkl', scaler_path='model/scaler.pkl'):
        """
        Save trained model and scaler
        """
        print("\n" + "="*50)
        print("SAVING MODEL")
        print("="*50)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        joblib.dump(self.model, model_path)
        print(f"Model saved to {model_path}")
        
        # Save scaler
        joblib.dump(self.scaler, scaler_path)
        print(f"Scaler saved to {scaler_path}")
        
        # Save feature names
        joblib.dump(self.features, 'model/features.pkl')
        print("Features saved to model/features.pkl")
    
    def load_model(self, model_path='model/model.pkl', scaler_path='model/scaler.pkl'):
        """
        Load trained model and scaler
        """
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.features = joblib.load('model/features.pkl')
        print("Model and components loaded successfully!")
    
    def predict_single(self, attendance, marks, behavior_score):
        """
        Predict dropout risk for a single student
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded!")
        
        # Calculate risk score
        risk_score = (100 - attendance) * 0.4 + (100 - marks) * 0.4 + (10 - behavior_score) * 2
        
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
            'risk_score': round(risk_score, 2)
        }

def main():
    """
    Main training pipeline
    """
    print("🎓 AI-DRIVEN STUDENT DROPOUT PREDICTION SYSTEM")
    print("=" * 60)
    print("Early Warning System for Reducing Student Dropout Rates")
    print("Aligned with NEP 2020 Objectives")
    print("=" * 60)
    
    # Initialize model
    predictor = DropoutPredictionModel()
    
    # Load data
    data = predictor.load_data('dataset/student_data.csv')
    
    # Exploratory analysis
    correlations = predictor.explore_data()
    
    # Preprocess data
    processed_data = predictor.preprocess_data()
    
    # Split data
    X_train, X_test, y_train, y_test = predictor.split_data()
    
    # Train model
    model = predictor.train_model(X_train, y_train)
    
    # Evaluate model
    results = predictor.evaluate_model(X_test, y_test)
    
    # Save model
    predictor.save_model()
    
    print("\n" + "="*60)
    print("🎉 MODEL TRAINING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"✅ Model Accuracy: {results['accuracy']*100:.2f}%")
    print(f"✅ Sensitivity: {results['sensitivity']*100:.2f}%")
    print(f"✅ Specificity: {results['specificity']*100:.2f}%")
    print(f"✅ Model saved to: model/model.pkl")
    print("="*60)
    
    return predictor

if __name__ == "__main__":
    model = main()
