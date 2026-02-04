# EduGuard - Student Dropout Prevention System

## Project Overview
EduGuard is an intelligent, data-driven web application designed to reduce student dropout rates. It monitors attendance and academic performance, identifies students at risk using a weighted rule-based algorithm, and provides early warning alerts to educators.

## Features
- **Dashboard:** Real-time overview of student statistics and risk distribution.
- **Risk Analysis:** Automated calculation of risk levels (Low, Medium, High) based on attendance and grades.
- **Student Profiles:** Detailed view of student history, including attendance logs and academic records.
- **Intervention Tracking:** Log and track counseling sessions or parent meetings.
- **Analytics:** Visual reports using Chart.js.

## Tech Stack
- **Backend:** Python Flask
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** HTML5, Bootstrap 5, Jinja2
- **Visualization:** Chart.js

## Project Structure
```
/student-dropout-prevention
  ├── app.py                 # Main application entry point
  ├── models.py              # Database models (User, Student, Attendance, etc.)
  ├── routes.py              # Route definitions and controllers
  ├── utils.py               # Risk calculation logic
  ├── config.py              # Configuration settings
  ├── seed_data.py           # Script to populate database with dummy data
  ├── requirements.txt       # Python dependencies
  ├── static/                # CSS, JS, Images
  └── templates/             # HTML Templates
```

## Setup Instructions

1. **Install Dependencies**
   Ensure you have Python installed. Run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   Run the seeder script to create the database and populate it with sample data:
   ```bash
   python seed_data.py
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

4. **Access the System**
   Open your browser and go to: `http://127.0.0.1:5000`
   
   **Login Credentials:**
   - Email: `admin@school.edu`
   - Password: `password`

## Risk Calculation Logic (Viva Explanation)
The system uses a weighted algorithm to determine the Risk Score (0-100):
- **Attendance Weight (60%):** Low attendance significantly increases risk.
- **Academic Weight (40%):** Low grades contribute to risk.
- **Critical Failure:** If attendance drops below 60%, the student is automatically flagged as **High Risk**.

Formula:
`RiskScore = (AttendanceRisk * 0.6) + (AcademicRisk * 0.4)`
Where Risk is inverted percentage (100 - Actual%).

## Future Scope
- Integration with Machine Learning models (Scikit-Learn) for predictive analysis.
- SMS/Email notifications for parents.
- Mobile App for students.
