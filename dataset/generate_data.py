import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_student_data(num_students=500):
    """
    Generate realistic student data for dropout prediction
    """
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    for i in range(num_students):
        # Generate realistic student profiles
        student_id = f"STU{str(i+1).zfill(4)}"
        
        # Attendance (60-100% with normal distribution)
        attendance = np.clip(np.random.normal(85, 10), 60, 100)
        
        # Academic performance (correlated with attendance)
        base_marks = (attendance / 100) * 85  # Base marks from attendance
        marks = np.clip(np.random.normal(base_marks, 15), 0, 100)
        
        # Behavior score (1-10, influenced by attendance and marks)
        behavior_base = (attendance / 100) * 6 + (marks / 100) * 3
        behavior_score = np.clip(np.random.normal(behavior_base, 2), 1, 10)
        
        # Calculate dropout probability based on multiple factors
        # Higher risk factors: low attendance, poor marks, bad behavior
        risk_factors = []
        
        # Attendance risk
        if attendance < 70:
            risk_factors.append(0.7)
        elif attendance < 80:
            risk_factors.append(0.4)
        else:
            risk_factors.append(0.1)
        
        # Academic risk
        if marks < 40:
            risk_factors.append(0.8)
        elif marks < 60:
            risk_factors.append(0.5)
        else:
            risk_factors.append(0.1)
        
        # Behavior risk
        if behavior_score < 4:
            risk_factors.append(0.6)
        elif behavior_score < 6:
            risk_factors.append(0.3)
        else:
            risk_factors.append(0.05)
        
        # Combined dropout probability
        dropout_prob = np.mean(risk_factors)
        
        # Add some randomness and make binary decision
        dropout_prob = np.clip(dropout_prob + np.random.normal(0, 0.1), 0, 1)
        dropout = 1 if dropout_prob > 0.5 else 0
        
        # Ensure we have a balanced dataset (approximately 30% dropout rate)
        if dropout == 1 and len([d for d in data if d['dropout'] == 1]) >= (num_students * 0.3):
            dropout = 0
        
        data.append({
            'student_id': student_id,
            'attendance': round(attendance, 1),
            'marks': round(marks, 1),
            'behavior_score': round(behavior_score, 1),
            'dropout': dropout
        })
    
    # Shuffle data to ensure randomness
    random.shuffle(data)
    
    return pd.DataFrame(data)

def save_dataset(df, filename):
    """Save dataset to CSV"""
    df.to_csv(filename, index=False)
    print(f"Dataset saved to {filename}")
    print(f"Total records: {len(df)}")
    print(f"Dropout students: {df['dropout'].sum()} ({df['dropout'].mean()*100:.1f}%)")
    print(f"Safe students: {len(df) - df['dropout'].sum()} ({(1-df['dropout'].mean())*100:.1f}%)")

if __name__ == "__main__":
    # Generate dataset
    print("Generating student dataset...")
    student_data = generate_student_data(500)
    
    # Display sample data
    print("\nSample data:")
    print(student_data.head(10))
    
    # Display statistics
    print("\nDataset Statistics:")
    print(student_data.describe())
    
    # Save to CSV
    save_dataset(student_data, 'dataset/student_data.csv')
    
    print("\nDataset generation completed successfully!")
