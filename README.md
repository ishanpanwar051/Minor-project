# EduGuard – Student Dropout Prevention System

## Core Purpose
Help institutions detect at-risk students early and provide personalized support to prevent dropouts. This is a holistic Student Dropout Prevention Platform — not just attendance classification.

## Main Features

### 1. Student Profile
- Name
- Attendance %
- Marks
- Family Pressure (Low/Medium/High)
- Financial Condition (Low/Medium/High)
- Health / Accident (Yes/No)
- Mental Stress Level
- Parent Name
- Parent Contact

### 2. Dropout Risk Prediction (Rule-Based AI)
Calculates risk using combined academic and personal factors:
- Attendance < 75
- Marks < 40
- Financial condition = Low
- Family pressure = High
- Health issue = Yes

Risk Levels: High / Medium / Low  
Also displays WHY the student is at risk (reasons list).

### 3. AI Driven Early Warning System
Dashboard shows:
- ⚠ Student at Risk of Dropout
- ⚠ Early Intervention Required
Highlights high-risk students in RED and suggests interventions.

### 4. Academic Challenges Module
Tracks:
- Poor grades
- Attendance issues
- Motivation loss
- Time management
- Subject difficulty
- Language barriers
- Technology access

### 5. Personal & Social Challenges Module
Tracks:
- Family problems
- Financial stress
- Mental health
- Health issues / accidents
- Bullying / isolation
- Peer pressure
- Cultural adjustment
- Work-study balance

### 6. Personalized Support System
Provides:
- Counseling sessions
- Academic tutoring
- Mentorship programs
- Flexible learning schedules
- Career guidance
- Mental health resources

### 7. Parent & Community Involvement
Shows parent name and contact.  
Message: “Parent notified for academic support”

### 8. Prevention Strategies
- Strong student-educator relationships
- Inclusive environment
- Flexible learning paths
- Career guidance
- Peer networks
- Confidence building
- Celebrate small achievements

### 9. Dashboard UI
Modern website with:
- Student cards
- Risk color coding: Red = High, Yellow = Medium, Green = Low
- Early Warning Panel
- Support suggestions

### 10. About
Explains academic, personal, and social challenges; early detection; and personalized support.  
Aligned with NEP 2020 goals of reducing dropout rates and ensuring retention till secondary education.

## Tech Stack
- Backend: Flask
- Database: SQLite (SQLAlchemy)
- Frontend: Bootstrap 5, Jinja2
- Visualization: Chart.js

## Run Locally
```bash
pip install -r requirements_ews.txt
python run.py
```

Open http://127.0.0.1:5000 and log in with the seeded demo accounts.
