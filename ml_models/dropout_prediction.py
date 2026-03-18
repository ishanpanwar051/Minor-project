import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import json
from datetime import datetime

class DropoutPredictionML:
    def __init__(self):
        self.models = {
            'logistic_regression': LogisticRegression(random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'neural_network': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        }
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_weights = {
            # Financial Factors (25% weight)
            'family_income_level': 0.05,
            'financial_difficulty': 0.08,
            'fee_payment_delays': 0.04,
            'part_time_job_dependency': 0.04,
            'financial_aid_received': 0.04,
            
            # Academic Factors (20% weight)
            'gpa': 0.06,
            'attendance_percentage': 0.06,
            'grades_trend': 0.03,
            'backlog_subjects': 0.03,
            'assignment_completion_rate': 0.02,
            
            # Psychological Factors (20% weight)
            'stress_anxiety_level': 0.06,
            'motivation_score': 0.05,
            'self_confidence_level': 0.04,
            'mental_health_score': 0.03,
            'counseling_sessions_attended': 0.02,
            
            # Family Factors (15% weight)
            'parent_involvement_level': 0.05,
            'family_conflicts_status': 0.04,
            'caregiving_responsibilities': 0.03,
            'family_earning_responsibility': 0.03,
            
            # Health Factors (10% weight)
            'chronic_illness_status': 0.03,
            'sleep_quality_score': 0.03,
            'nutrition_habits_score': 0.02,
            'healthcare_access': 0.02,
            
            # Institutional Factors (5% weight)
            'teacher_student_relationship': 0.02,
            'mentorship_availability': 0.01,
            'student_satisfaction_score': 0.01,
            'institutional_support': 0.01,
            
            # Extracurricular Factors (3% weight)
            'clubs_participation': 0.01,
            'sports_participation': 0.01,
            'leadership_roles': 0.01,
            
            # Technology Factors (2% weight)
            'laptop_access': 0.01,
            'internet_quality': 0.01
        }
        
    def prepare_data(self, students_data):
        """Prepare data for ML training"""
        df = pd.DataFrame(students_data)
        
        # Create target variable (dropout risk)
        df['dropout_risk'] = df.apply(self._calculate_dropout_risk, axis=1)
        
        # Handle categorical variables
        categorical_columns = [
            'family_income_level', 'grades_trend', 'peer_relationship_quality',
            'family_conflicts_status', 'chronic_illness_status', 'disability_status',
            'teacher_feedback_quality', 'institutional_support', 'peer_group_involvement',
            'internet_quality', 'loan_status', 'project_submission_status',
            'mental_health_status', 'curriculum_flexibility', 'device_loan_status'
        ]
        
        # Convert boolean columns to int
        boolean_columns = [
            'scholarship_eligibility', 'part_time_job_dependency', 'financial_aid_received',
            'remedial_classes_participation', 'caregiving_responsibilities', 'family_earning_responsibility',
            'healthcare_access', 'mentorship_availability', 'clubs_participation',
            'sports_participation', 'leadership_roles', 'laptop_access', 'smartphone_access'
        ]
        
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].astype(int)
        
        # Handle categorical columns
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown')
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    # Fit on all possible values
                    unique_values = df[col].unique()
                    self.label_encoders[col].fit(unique_values)
                df[col] = self.label_encoders[col].transform(df[col])
        
        # Handle missing values for numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col != 'dropout_risk':  # Don't fill target variable
                df[col] = df[col].fillna(df[col].median())
        
        # Ensure all data is numeric and handle any remaining NaN values
        for col in df.columns:
            if col == 'dropout_risk':
                continue
            if df[col].dtype == 'object':
                # Try to convert to numeric, if fails, use label encoding
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
            
            # Fill any remaining NaN values
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median() if df[col].dtype in ['int64', 'float64'] else 0)
        
        # Final check for any remaining NaN values
        df = df.fillna(0)
        
        return df
    
    def _calculate_dropout_risk(self, student):
        """Calculate dropout risk based on multiple factors"""
        risk_score = 0
        
        # Financial risk factors
        if student.get('financial_difficulty', 5) >= 8:
            risk_score += 25
        if student.get('fee_payment_delays', 0) > 2:
            risk_score += 15
        if student.get('part_time_job_dependency', False):
            risk_score += 10
            
        # Academic risk factors
        if student.get('gpa', 8) < 6.0:
            risk_score += 20
        if student.get('attendance_percentage', 85) < 70:
            risk_score += 20
        if student.get('backlog_subjects', 0) > 2:
            risk_score += 15
            
        # Psychological risk factors
        if student.get('stress_anxiety_level', 5) >= 8:
            risk_score += 20
        if student.get('motivation_score', 7) <= 3:
            risk_score += 15
        if student.get('self_confidence_level', 7) <= 3:
            risk_score += 10
            
        # Family risk factors
        if student.get('family_conflicts_status') == 'Severe':
            risk_score += 15
        if student.get('caregiving_responsibilities', False):
            risk_score += 10
        if student.get('family_earning_responsibility', False):
            risk_score += 10
            
        # Health risk factors
        if student.get('chronic_illness_status') == 'Severe':
            risk_score += 10
        if student.get('sleep_quality_score', 7) <= 3:
            risk_score += 8
        if student.get('nutrition_habits_score', 7) <= 3:
            risk_score += 7
            
        # Institutional risk factors
        if student.get('teacher_student_relationship', 7) <= 3:
            risk_score += 8
        if not student.get('mentorship_availability', False):
            risk_score += 5
            
        # Technology risk factors
        if not student.get('laptop_access', True):
            risk_score += 10
        if student.get('internet_quality') == 'Poor':
            risk_score += 8
        
        # Convert to binary classification (0 = Low Risk, 1 = High Risk)
        return 1 if risk_score >= 50 else 0
    
    def train_models(self, X, y):
        """Train all ML models"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {}
        
        for name, model in self.models.items():
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Predictions
            y_pred = model.predict(X_test_scaled)
            
            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'classification_report': report,
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
            }
        
        return results, X_test_scaled, y_test
    
    def predict_dropout_risk(self, student_data, model_name='random_forest'):
        """Predict dropout risk for a single student"""
        # Prepare data
        df = pd.DataFrame([student_data])
        
        # Handle boolean columns
        boolean_columns = [
            'scholarship_eligibility', 'part_time_job_dependency', 'financial_aid_received',
            'remedial_classes_participation', 'caregiving_responsibilities', 'family_earning_responsibility',
            'healthcare_access', 'mentorship_availability', 'clubs_participation',
            'sports_participation', 'leadership_roles', 'laptop_access', 'smartphone_access'
        ]
        
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].astype(int)
        
        # Handle categorical variables
        for col, encoder in self.label_encoders.items():
            if col in df.columns:
                value = df[col].iloc[0]
                if value not in encoder.classes_:
                    # Handle unseen categories by adding to encoder
                    encoder.classes_ = np.append(encoder.classes_, value)
                try:
                    df[col] = encoder.transform([value])[0]
                except:
                    df[col] = 0  # Default value if transformation fails
        
        # Handle any remaining string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    df[col] = 0  # Default value
        
        # Fill any NaN values
        df = df.fillna(0)
        
        # Ensure all columns are numeric
        for col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                df[col] = 0
        
        # Scale features
        X_scaled = self.scaler.transform(df)
        
        # Predict
        model = self.models[model_name]
        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]
        
        # Calculate weighted risk score
        risk_score = self._calculate_weighted_risk_score(student_data)
        
        return {
            'prediction': int(prediction),
            'probability': float(probability[1]),
            'risk_level': 'High' if prediction == 1 else 'Low',
            'risk_score': risk_score,
            'model_used': model_name
        }
    
    def _calculate_weighted_risk_score(self, student_data):
        """Calculate weighted risk score based on feature importance"""
        risk_score = 0
        
        for feature, weight in self.feature_weights.items():
            if feature in student_data:
                value = student_data[feature]
                
                # Normalize different types of features
                if isinstance(value, bool):
                    normalized_value = 1 if value else 0
                elif isinstance(value, (int, float)):
                    # Normalize to 0-1 scale
                    if feature in ['gpa', 'attendance_percentage', 'motivation_score', 
                                  'self_confidence_level', 'sleep_quality_score', 'nutrition_habits_score',
                                  'teacher_student_relationship', 'student_satisfaction_score']:
                        normalized_value = max(0, min(1, (10 - value) / 10))  # Higher is better
                    elif feature in ['stress_anxiety_level', 'financial_difficulty', 
                                   'fee_payment_delays', 'backlog_subjects']:
                        normalized_value = min(1, value / 10)  # Higher is worse
                    else:
                        normalized_value = value / 10  # Default normalization
                else:
                    # Categorical variables
                    if feature in ['family_income_level']:
                        normalized_value = {'Low': 0.8, 'Medium': 0.5, 'High': 0.2}.get(value, 0.5)
                    elif feature in ['grades_trend']:
                        normalized_value = {'Declining': 0.8, 'Stable': 0.5, 'Improving': 0.2}.get(value, 0.5)
                    else:
                        normalized_value = 0.5  # Default
                
                risk_score += normalized_value * weight * 100
        
        return min(100, risk_score)
    
    def save_models(self, filepath='ml_models/'):
        """Save trained models"""
        import os
        os.makedirs(filepath, exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, f'{filepath}{name}_model.pkl')
        
        # Save scaler and encoders
        joblib.dump(self.scaler, f'{filepath}scaler.pkl')
        joblib.dump(self.label_encoders, f'{filepath}label_encoders.pkl')
        joblib.dump(self.feature_weights, f'{filepath}feature_weights.pkl')
    
    def load_models(self, filepath='ml_models/'):
        """Load trained models"""
        # Load models
        for name in self.models.keys():
            self.models[name] = joblib.load(f'{filepath}{name}_model.pkl')
        
        # Load scaler and encoders
        self.scaler = joblib.load(f'{filepath}scaler.pkl')
        self.label_encoders = joblib.load(f'{filepath}label_encoders.pkl')
        self.feature_weights = joblib.load(f'{filepath}feature_weights.pkl')

# Sample usage and training data generator
def generate_sample_training_data():
    """Generate sample training data for ML models"""
    np.random.seed(42)
    n_samples = 1000
    
    data = []
    for i in range(n_samples):
        student = {
            # Financial factors
            'family_income_level': np.random.choice(['Low', 'Medium', 'High'], p=[0.4, 0.4, 0.2]),
            'financial_difficulty': np.random.randint(1, 11),
            'fee_payment_delays': np.random.randint(0, 6),
            'part_time_job_dependency': np.random.choice([True, False], p=[0.3, 0.7]),
            'financial_aid_received': np.random.choice([True, False], p=[0.4, 0.6]),
            'loan_status': np.random.choice(['None', 'Requested', 'Approved', 'Rejected'], p=[0.5, 0.2, 0.2, 0.1]),
            
            # Academic factors
            'gpa': np.random.uniform(4.0, 10.0),
            'attendance_percentage': np.random.uniform(50, 100),
            'grades_trend': np.random.choice(['Improving', 'Stable', 'Declining'], p=[0.3, 0.4, 0.3]),
            'backlog_subjects': np.random.randint(0, 5),
            'assignment_completion_rate': np.random.uniform(60, 100),
            'project_submission_status': np.random.choice(['On Time', 'Late', 'Missing'], p=[0.6, 0.3, 0.1]),
            
            # Psychological factors
            'stress_anxiety_level': np.random.randint(1, 11),
            'motivation_score': np.random.randint(1, 11),
            'self_confidence_level': np.random.randint(1, 11),
            'mental_health_score': np.random.randint(1, 11),
            'counseling_sessions_attended': np.random.randint(0, 10),
            
            # Family factors
            'parent_involvement_level': np.random.choice(['High', 'Medium', 'Low'], p=[0.3, 0.4, 0.3]),
            'family_conflicts_status': np.random.choice(['None', 'Moderate', 'Severe'], p=[0.5, 0.3, 0.2]),
            'caregiving_responsibilities': np.random.choice([True, False], p=[0.2, 0.8]),
            'family_earning_responsibility': np.random.choice([True, False], p=[0.15, 0.85]),
            
            # Health factors
            'chronic_illness_status': np.random.choice(['None', 'Mild', 'Severe'], p=[0.6, 0.3, 0.1]),
            'sleep_quality_score': np.random.randint(1, 11),
            'nutrition_habits_score': np.random.randint(1, 11),
            'healthcare_access': np.random.choice([True, False], p=[0.8, 0.2]),
            
            # Institutional factors
            'teacher_student_relationship': np.random.randint(1, 11),
            'mentorship_availability': np.random.choice([True, False], p=[0.6, 0.4]),
            'student_satisfaction_score': np.random.randint(1, 11),
            'teacher_feedback_quality': np.random.choice(['Good', 'Average', 'Poor'], p=[0.4, 0.4, 0.2]),
            'institutional_support': np.random.choice(['High', 'Medium', 'Low'], p=[0.3, 0.4, 0.3]),
            
            # Extracurricular factors
            'clubs_participation': np.random.choice([True, False], p=[0.5, 0.5]),
            'sports_participation': np.random.choice([True, False], p=[0.4, 0.6]),
            'leadership_roles': np.random.choice([True, False], p=[0.2, 0.8]),
            
            # Technology factors
            'laptop_access': np.random.choice([True, False], p=[0.8, 0.2]),
            'internet_quality': np.random.choice(['Good', 'Average', 'Poor'], p=[0.5, 0.3, 0.2])
        }
        data.append(student)
    
    return data

if __name__ == "__main__":
    # Initialize ML system
    ml_system = DropoutPredictionML()
    
    # Generate training data
    training_data = generate_sample_training_data()
    
    # Prepare data
    df = ml_system.prepare_data(training_data)
    
    # Split features and target
    X = df.drop('dropout_risk', axis=1)
    y = df['dropout_risk']
    
    # Train models
    results, X_test, y_test = ml_system.train_models(X, y)
    
    # Print results
    print("🎯 ML Model Training Results:")
    print("=" * 50)
    
    for name, result in results.items():
        print(f"\n📊 {name.upper()}:")
        print(f"   Accuracy: {result['accuracy']:.4f}")
        print(f"   Precision: {result['classification_report']['weighted avg']['precision']:.4f}")
        print(f"   Recall: {result['classification_report']['weighted avg']['recall']:.4f}")
        print(f"   F1-Score: {result['classification_report']['weighted avg']['f1-score']:.4f}")
    
    # Save models
    ml_system.save_models()
    
    # Test prediction
    test_student = training_data[0]
    prediction = ml_system.predict_dropout_risk(test_student)
    
    print(f"\n🔮 Sample Prediction:")
    print(f"   Risk Level: {prediction['risk_level']}")
    print(f"   Risk Score: {prediction['risk_score']:.2f}")
    print(f"   Probability: {prediction['probability']:.4f}")
    print(f"   Model Used: {prediction['model_used']}")
