from datetime import date, datetime, timedelta
import json
import random

from app import create_app
from models import (
    Alert,
    ApplicationStatus,
    Attendance,
    CounsellingRequest,
    CounsellingStatus,
    RiskProfile,
    Scholarship,
    ScholarshipApplication,
    ScholarshipStatus,
    Student,
    User,
    db,
)
from models_parent import ParentMessage
from models_support import MoodLog, StudentGoal


PEOPLE = [
    {
        "student_id": "ST101",
        "first_name": "Aarav",
        "last_name": "Sharma",
        "email": "aarav.sharma@eduguard.edu",
        "department": "Computer Science",
        "year": 2,
        "semester": 4,
        "gpa": 8.7,
        "attendance": 92,
        "academic": 88,
        "income": 42000,
        "need": "Medium",
        "mental": 9,
    },
    {
        "student_id": "ST102",
        "first_name": "Ananya",
        "last_name": "Verma",
        "email": "ananya.verma@eduguard.edu",
        "department": "Engineering",
        "year": 3,
        "semester": 5,
        "gpa": 7.9,
        "attendance": 84,
        "academic": 79,
        "income": 28000,
        "need": "High",
        "financial": True,
        "mental": 7,
    },
    {
        "student_id": "ST103",
        "first_name": "Rohan",
        "last_name": "Mehta",
        "email": "rohan.mehta@eduguard.edu",
        "department": "Business",
        "year": 1,
        "semester": 2,
        "gpa": 6.8,
        "attendance": 72,
        "academic": 64,
        "income": 52000,
        "need": "Low",
        "family": True,
        "mental": 6,
    },
    {
        "student_id": "ST104",
        "first_name": "Priya",
        "last_name": "Nair",
        "email": "priya.nair@eduguard.edu",
        "department": "Arts",
        "year": 2,
        "semester": 3,
        "gpa": 8.1,
        "attendance": 88,
        "academic": 82,
        "income": 36000,
        "need": "Medium",
        "mental": 8,
    },
    {
        "student_id": "ST105",
        "first_name": "Kabir",
        "last_name": "Khan",
        "email": "kabir.khan@eduguard.edu",
        "department": "Science",
        "year": 4,
        "semester": 7,
        "gpa": 5.9,
        "attendance": 58,
        "academic": 48,
        "income": 21000,
        "need": "High",
        "financial": True,
        "health": True,
        "mental": 4,
    },
    {
        "student_id": "ST106",
        "first_name": "Meera",
        "last_name": "Iyer",
        "email": "meera.iyer@eduguard.edu",
        "department": "Computer Science",
        "year": 3,
        "semester": 6,
        "gpa": 9.1,
        "attendance": 95,
        "academic": 93,
        "income": 68000,
        "need": "Low",
        "mental": 9,
    },
    {
        "student_id": "ST107",
        "first_name": "Dev",
        "last_name": "Patel",
        "email": "dev.patel@eduguard.edu",
        "department": "Engineering",
        "year": 2,
        "semester": 4,
        "gpa": 6.2,
        "attendance": 65,
        "academic": 55,
        "income": 25000,
        "need": "High",
        "financial": True,
        "social": True,
        "mental": 5,
    },
    {
        "student_id": "ST108",
        "first_name": "Sara",
        "last_name": "Thomas",
        "email": "sara.thomas@eduguard.edu",
        "department": "Business",
        "year": 3,
        "semester": 5,
        "gpa": 7.4,
        "attendance": 81,
        "academic": 74,
        "income": 44000,
        "need": "Medium",
        "mental": 7,
    },
]


SCHOLARSHIPS = [
    {
        "title": "EduGuard Merit Excellence Scholarship",
        "description": "For students with strong academic records and consistent attendance.",
        "provider": "EduGuard Foundation",
        "amount": 6000,
        "min_gpa": 7.5,
        "max_income": 80000,
        "departments": ["Computer Science", "Engineering", "Science", "Business"],
        "year_level": "All Years",
        "tags": ["merit", "academic"],
    },
    {
        "title": "Financial Support Grant",
        "description": "Need-based support for students with financial constraints.",
        "provider": "Student Aid Trust",
        "amount": 3500,
        "min_gpa": 5.5,
        "max_income": 30000,
        "departments": ["All Departments"],
        "year_level": "All Years",
        "tags": ["need-based", "financial-aid"],
    },
    {
        "title": "Women in STEM Award",
        "description": "Encourages women pursuing technology, science, and engineering careers.",
        "provider": "STEM Futures",
        "amount": 5000,
        "min_gpa": 7.0,
        "max_income": 90000,
        "departments": ["Computer Science", "Engineering", "Science"],
        "year_level": "Sophomore",
        "tags": ["stem", "leadership"],
    },
]


def ensure_user_and_student(person):
    user = User.query.filter_by(email=person["email"]).first()
    if not user:
        user = User(
            username=person["student_id"].lower(),
            email=person["email"],
            role="student",
        )
        user.set_password("student123")
        db.session.add(user)
        db.session.flush()

    student = Student.query.filter_by(student_id=person["student_id"]).first()
    if not student:
        student = Student(
            user_id=user.id,
            student_id=person["student_id"],
            first_name=person["first_name"],
            last_name=person["last_name"],
            email=person["email"],
            department=person["department"],
            year=person["year"],
            semester=person["semester"],
            enrollment_date=date.today() - timedelta(days=365 * max(person["year"], 1)),
            parent_name=f"{person['last_name']} Guardian",
            parent_email=f"parent.{person['student_id'].lower()}@example.com",
            parent_phone=f"90000{random.randint(10000, 99999)}",
        )
        db.session.add(student)
        db.session.flush()

    student.user_id = user.id
    student.gpa = person["gpa"]
    student.department = person["department"]
    student.year = person["year"]
    student.semester = person["semester"]
    student.attendance_rate = person["attendance"]
    student.annual_income = person["income"]
    student.financial_need_level = person["need"]
    student.credits_completed = max(20, person["year"] * 28)
    student.career_interests = career_interests_for(person["department"])
    return user, student


def career_interests_for(department):
    if department == "Computer Science":
        return "Software Engineering, AI, Cloud Computing"
    if department == "Engineering":
        return "Design Engineering, Robotics, Project Management"
    if department == "Business":
        return "Finance, Marketing, Entrepreneurship"
    if department == "Science":
        return "Research, Data Analysis, Laboratory Science"
    return "Creative Writing, Communication, Public Policy"


def ensure_risk_profile(student, person):
    risk = RiskProfile.query.filter_by(student_id=student.id).first()
    if not risk:
        risk = RiskProfile(student_id=student.id)
        db.session.add(risk)

    risk.attendance_rate = person["attendance"]
    risk.academic_performance = person["academic"]
    risk.financial_issues = person.get("financial", False)
    risk.family_problems = person.get("family", False)
    risk.health_issues = person.get("health", False)
    risk.social_isolation = person.get("social", False)
    risk.mental_wellbeing_score = person["mental"]
    risk.update_risk_score(use_ml=False)
    return risk


def ensure_attendance(student, attendance_rate):
    existing_dates = {
        item.date
        for item in Attendance.query.filter(
            Attendance.student_id == student.id,
            Attendance.date >= date.today() - timedelta(days=30),
        ).all()
    }
    for days_ago in range(30):
        entry_date = date.today() - timedelta(days=days_ago)
        if entry_date in existing_dates:
            continue
        present_probability = attendance_rate / 100
        status = "Present" if random.random() <= present_probability else random.choice(["Absent", "Late"])
        db.session.add(
            Attendance(
                student_id=student.id,
                date=entry_date,
                status=status,
                course=random.choice(["Math 201", "CS 210", "ENG 110", "BUS 120", "SCI 150"]),
            )
        )


def ensure_support_data(student):
    if not StudentGoal.query.filter_by(student_id=student.id).first():
        goals = [
            ("Improve attendance", "Attend every class this week", 45),
            ("Complete assignment", "Submit pending coursework before deadline", 70),
        ]
        for title, description, progress in goals:
            db.session.add(
                StudentGoal(
                    student_id=student.id,
                    title=title,
                    description=description,
                    progress=progress,
                    target_date=date.today() + timedelta(days=random.randint(7, 28)),
                )
            )

    existing_moods = {
        item.log_date for item in MoodLog.query.filter_by(student_id=student.id).all()
    }
    for days_ago in range(7):
        log_date = date.today() - timedelta(days=days_ago)
        if log_date not in existing_moods:
            db.session.add(
                MoodLog(
                    student_id=student.id,
                    mood_score=random.randint(3, 5),
                    note=random.choice(["Focused today", "Need help with studies", "Feeling motivated", "Busy week"]),
                    log_date=log_date,
                )
            )


def ensure_alerts_and_messages(student, risk):
    if risk.risk_level in ["High", "Critical"]:
        title = f"{risk.risk_level} Risk Alert - {student.first_name} {student.last_name}"
        if not Alert.query.filter_by(student_id=student.id, title=title).first():
            db.session.add(
                Alert(
                    student_id=student.id,
                    alert_type="Risk",
                    severity=risk.risk_level,
                    title=title,
                    description=f"Risk score is {risk.risk_score:.1f}. Follow-up recommended.",
                    status="Active",
                )
            )

    if not ParentMessage.query.filter_by(student_id=student.id).first():
        db.session.add(
            ParentMessage(
                student_id=student.id,
                sender_role="faculty",
                sender_name="Dr. Faculty Mentor",
                message=f"Progress update for {student.first_name}: please monitor attendance and coursework.",
            )
        )


def ensure_counselling(user, student, risk):
    if CounsellingRequest.query.filter_by(student_id=student.id).first():
        return
    needs_help = risk.risk_level in ["High", "Critical"]
    db.session.add(
        CounsellingRequest(
            student_id=student.id,
            user_id=user.id,
            status=CounsellingStatus.SCHEDULED if needs_help else CounsellingStatus.REQUESTED,
            priority="high" if needs_help else "medium",
            counselling_type="Academic" if not needs_help else "Wellbeing",
            topic="Academic planning and student support",
            description="Student requested guidance for academic progress and support planning.",
            preferred_date=datetime.utcnow() + timedelta(days=3),
            scheduled_date=datetime.utcnow() + timedelta(days=5) if needs_help else None,
            ai_sentiment_score=0.45 if needs_help else 0.75,
            ai_urgency_score=0.85 if needs_help else 0.35,
            ai_topic_classification="Risk Support" if needs_help else "Academic Guidance",
        )
    )


def ensure_scholarships(admin_user):
    created = []
    for item in SCHOLARSHIPS:
        scholarship = Scholarship.query.filter_by(title=item["title"]).first()
        if not scholarship:
            scholarship = Scholarship(
                title=item["title"],
                description=item["description"],
                provider=item["provider"],
                amount=item["amount"],
                currency="USD",
                payment_frequency="Annual",
                min_gpa=item["min_gpa"],
                max_income=item["max_income"],
                required_credits=20,
                departments=json.dumps(item["departments"]),
                year_level=item["year_level"],
                nationality_requirements="All",
                gender_requirements="All",
                application_deadline=datetime.utcnow() + timedelta(days=random.randint(20, 75)),
                required_documents=json.dumps(["Transcript", "Statement of Purpose", "ID Proof"]),
                application_process="Submit online application and supporting documents.",
                status=ScholarshipStatus.ACTIVE,
                created_by=admin_user.id if admin_user else None,
                ai_tags=json.dumps(item["tags"]),
            )
            db.session.add(scholarship)
        created.append(scholarship)
    db.session.flush()
    return created


def ensure_applications(student, scholarships):
    for index, scholarship in enumerate(scholarships):
        if ScholarshipApplication.query.filter_by(student_id=student.id, scholarship_id=scholarship.id).first():
            continue
        status = [ApplicationStatus.PENDING, ApplicationStatus.UNDER_REVIEW, ApplicationStatus.APPROVED][index % 3]
        db.session.add(
            ScholarshipApplication(
                scholarship_id=scholarship.id,
                student_id=student.id,
                status=status,
                application_date=datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                personal_statement=f"I am applying for {scholarship.title} to continue my education with focus and consistency.",
                financial_justification="This support will help me cover academic expenses and reduce family burden.",
                ai_eligibility_score=random.randint(68, 95),
                ai_success_probability=random.uniform(0.55, 0.9),
                ai_recommendations="Strong fit based on profile and academic history.",
                gpa_at_application=student.gpa,
            )
        )


def seed_persons_data():
    random.seed(42)
    app = create_app()
    with app.app_context():
        admin_user = User.query.filter_by(email="admin@eduguard.edu").first()
        scholarships = ensure_scholarships(admin_user)

        added_or_updated = []
        for person in PEOPLE:
            user, student = ensure_user_and_student(person)
            risk = ensure_risk_profile(student, person)
            ensure_attendance(student, person["attendance"])
            ensure_support_data(student)
            ensure_alerts_and_messages(student, risk)
            ensure_counselling(user, student, risk)
            ensure_applications(student, scholarships[:2])
            added_or_updated.append((student, risk))

        db.session.commit()

        print("Persons data seeded successfully.")
        print(f"Students added/updated: {len(added_or_updated)}")
        print(f"Scholarships available: {len(scholarships)}")
        print("Student password for all seeded persons: student123")
        for student, risk in added_or_updated:
            print(f"- {student.student_id}: {student.first_name} {student.last_name} | {student.email} | Risk: {risk.risk_level}")


if __name__ == "__main__":
    seed_persons_data()
