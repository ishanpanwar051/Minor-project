"""Demo data and live metric helpers for EduGuard.

The project is used for classroom demos, so this module keeps the local
database populated with realistic records instead of empty/static dashboards.
"""

from datetime import date, datetime, timedelta

from models import (
    ApplicationStatus,
    Attendance,
    CounsellingRequest,
    CounsellingStatus,
    Notification,
    RiskProfile,
    Scholarship,
    ScholarshipApplication,
    ScholarshipStatus,
    Student,
    User,
    db,
)


DEMO_STUDENTS = [
    {
        "student_id": "ST001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@eduguard.edu",
        "department": "Computer Science",
        "gpa": 8.6,
        "attendance_rate": 92,
        "financial_issues": False,
        "family_problems": False,
        "health_issues": False,
        "social_isolation": False,
        "mental_wellbeing_score": 9,
        "annual_income": 850000,
        "financial_need_level": "Low",
    },
    {
        "student_id": "ST002",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@eduguard.edu",
        "department": "Engineering",
        "gpa": 7.1,
        "attendance_rate": 76,
        "financial_issues": True,
        "family_problems": False,
        "health_issues": False,
        "social_isolation": False,
        "mental_wellbeing_score": 6,
        "annual_income": 280000,
        "financial_need_level": "High",
    },
    {
        "student_id": "ST003",
        "first_name": "Rohit",
        "last_name": "Verma",
        "email": "rohit.verma@eduguard.edu",
        "department": "Business",
        "gpa": 5.4,
        "attendance_rate": 58,
        "financial_issues": True,
        "family_problems": True,
        "health_issues": False,
        "social_isolation": False,
        "mental_wellbeing_score": 4,
        "annual_income": 180000,
        "financial_need_level": "High",
    },
    {
        "student_id": "ST004",
        "first_name": "Sara",
        "last_name": "Khan",
        "email": "sara.khan@eduguard.edu",
        "department": "Arts",
        "gpa": 6.2,
        "attendance_rate": 68,
        "financial_issues": False,
        "family_problems": True,
        "health_issues": False,
        "social_isolation": True,
        "mental_wellbeing_score": 5,
        "annual_income": 420000,
        "financial_need_level": "Medium",
    },
    {
        "student_id": "ST005",
        "first_name": "Alex",
        "last_name": "Brown",
        "email": "alex.brown@eduguard.edu",
        "department": "Science",
        "gpa": 4.2,
        "attendance_rate": 28,
        "financial_issues": True,
        "family_problems": False,
        "health_issues": True,
        "social_isolation": True,
        "mental_wellbeing_score": 3,
        "annual_income": 140000,
        "financial_need_level": "High",
    },
]


GENERATED_FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Ishaan", "Kabir", "Arjun", "Riya", "Ananya",
    "Diya", "Meera", "Kavya", "Nisha", "Priya", "Neha", "Rahul", "Aman",
    "Yash", "Kunal", "Sakshi", "Isha", "Tanvi", "Mohit", "Naman", "Tanya",
    "Dev", "Harsh", "Kartik", "Palak", "Simran", "Varun",
]

GENERATED_LAST_NAMES = [
    "Sharma", "Patel", "Gupta", "Singh", "Yadav", "Mehta", "Jain", "Khan",
    "Verma", "Joshi", "Mishra", "Rathore", "Choudhary", "Malviya", "Panwar",
]

GENERATED_DEPARTMENTS = [
    "Computer Science",
    "Engineering",
    "Business",
    "Arts",
    "Science",
    "Information Technology",
    "Data Science",
    "Commerce",
]


def generated_student_rows(total=80):
    rows = list(DEMO_STUDENTS)
    for number in range(len(DEMO_STUDENTS) + 1, total + 1):
        first = GENERATED_FIRST_NAMES[(number - 1) % len(GENERATED_FIRST_NAMES)]
        last = GENERATED_LAST_NAMES[(number * 2) % len(GENERATED_LAST_NAMES)]
        department = GENERATED_DEPARTMENTS[(number - 1) % len(GENERATED_DEPARTMENTS)]

        if number % 11 == 0:
            gpa = 4.1
            attendance = 32
            financial = True
            family = True
            health = True
            isolation = True
            wellbeing = 3
            need = "High"
            income = 160000
        elif number % 7 == 0:
            gpa = 5.2
            attendance = 55
            financial = True
            family = number % 14 == 0
            health = False
            isolation = True
            wellbeing = 4
            need = "High"
            income = 220000
        elif number % 5 == 0:
            gpa = 6.3
            attendance = 68
            financial = number % 10 == 0
            family = True
            health = False
            isolation = False
            wellbeing = 6
            need = "Medium"
            income = 420000
        elif number % 3 == 0:
            gpa = 7.2
            attendance = 78
            financial = False
            family = False
            health = False
            isolation = False
            wellbeing = 7
            need = "Medium"
            income = 600000
        else:
            gpa = 8.1 + ((number % 5) * 0.2)
            attendance = 86 + (number % 9)
            financial = False
            family = False
            health = False
            isolation = False
            wellbeing = 8 + (number % 3)
            need = "Low"
            income = 850000

        rows.append({
            "student_id": f"ST{number:03d}",
            "first_name": first,
            "last_name": last,
            "email": f"student{number:03d}@eduguard.edu",
            "department": department,
            "gpa": round(gpa, 1),
            "attendance_rate": attendance,
            "financial_issues": financial,
            "family_problems": family,
            "health_issues": health,
            "social_isolation": isolation,
            "mental_wellbeing_score": wellbeing,
            "annual_income": income,
            "financial_need_level": need,
        })
    return rows


DEMO_SCHOLARSHIPS = [
    {
        "title": "Merit Excellence Grant",
        "provider": "EduGuard Foundation",
        "amount": 50000,
        "min_gpa": 8.0,
        "max_income": 1200000,
        "departments": ["Computer Science", "Engineering", "Science"],
        "tags": "merit,academic",
    },
    {
        "title": "Need Based Support Fund",
        "provider": "Student Welfare Cell",
        "amount": 35000,
        "min_gpa": 5.0,
        "max_income": 300000,
        "departments": ["Computer Science", "Engineering", "Business", "Arts", "Science"],
        "tags": "financial,need",
    },
    {
        "title": "Women in Technology Scholarship",
        "provider": "TechFuture India",
        "amount": 45000,
        "min_gpa": 6.5,
        "max_income": 900000,
        "departments": ["Computer Science", "Engineering"],
        "tags": "technology,women",
    },
    {
        "title": "Attendance Improvement Aid",
        "provider": "Academic Support Office",
        "amount": 18000,
        "min_gpa": 4.0,
        "max_income": 500000,
        "departments": ["Business", "Arts", "Science", "Engineering"],
        "tags": "attendance,retention",
    },
]


def normalize_gpa_to_percent(gpa):
    if not gpa:
        return 0.0
    if gpa <= 4:
        return min(100.0, (gpa / 4.0) * 100.0)
    return min(100.0, (gpa / 10.0) * 100.0)


def attendance_percentage(student_id, days=60):
    since = date.today() - timedelta(days=days)
    records = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.date >= since,
    ).all()
    if not records:
        return None
    earned = 0.0
    for record in records:
        if record.status == "Present":
            earned += 1
        elif record.status in {"Late", "Excused"}:
            earned += 0.5
    return round((earned / len(records)) * 100, 1)


def sync_student_risk_inputs(student):
    risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
    if not risk_profile:
        risk_profile = RiskProfile(student_id=student.id)
        db.session.add(risk_profile)

    live_attendance = attendance_percentage(student.id)
    if live_attendance is not None:
        risk_profile.attendance_rate = live_attendance
        student.attendance_rate = live_attendance
    elif student.attendance_rate is not None:
        risk_profile.attendance_rate = student.attendance_rate

    risk_profile.academic_performance = normalize_gpa_to_percent(student.gpa)
    risk_profile.update_risk_score(use_ml=False)
    return risk_profile


def _ensure_user(email, username, role, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
    else:
        user.username = user.username or username
        user.role = role
        user.is_active = True
    return user


def _ensure_demo_student(data):
    user = _ensure_user(data["email"], data["student_id"].lower(), "student", "student123")
    student = Student.query.filter_by(student_id=data["student_id"]).first()
    if not student:
        student = Student(
            user_id=user.id,
            student_id=data["student_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            enrollment_date=date(2022, 9, 1),
            expected_graduation=date(2026, 6, 30),
            year=2,
            semester=4,
            credits_completed=60,
        )
        db.session.add(student)
        db.session.flush()

    student.user_id = user.id
    student.first_name = data["first_name"]
    student.last_name = data["last_name"]
    student.email = data["email"]
    student.department = data["department"]
    student.gpa = data["gpa"]
    student.attendance_rate = data["attendance_rate"]
    student.annual_income = data["annual_income"]
    student.financial_need_level = data["financial_need_level"]
    student.academic_standing = "Good" if data["gpa"] >= 7 else "Needs Support"
    student.parent_name = f"Parent of {data['first_name']}"
    student.parent_email = f"parent.{data['first_name'].lower()}@example.com"
    student.parent_phone = "9876543210"

    Attendance.query.filter_by(student_id=student.id).delete()
    present_target = int(round((data["attendance_rate"] / 100) * 40))
    for i in range(40):
        if i < present_target:
            status = "Present"
        elif i % 5 == 0:
            status = "Late"
        else:
            status = "Absent"
        db.session.add(
            Attendance(
                student_id=student.id,
                date=date.today() - timedelta(days=i),
                status=status,
                course=f"{data['department']} Core",
            )
        )

    risk_profile = RiskProfile.query.filter_by(student_id=student.id).first()
    if not risk_profile:
        risk_profile = RiskProfile(student_id=student.id)
        db.session.add(risk_profile)
    risk_profile.financial_issues = data["financial_issues"]
    risk_profile.family_problems = data["family_problems"]
    risk_profile.health_issues = data["health_issues"]
    risk_profile.social_isolation = data["social_isolation"]
    risk_profile.mental_wellbeing_score = data["mental_wellbeing_score"]
    risk_profile.attendance_rate = data["attendance_rate"]
    risk_profile.academic_performance = normalize_gpa_to_percent(data["gpa"])
    risk_profile.update_risk_score(use_ml=False)
    return student


def _ensure_scholarship(data, admin_id):
    import json

    scholarship = Scholarship.query.filter_by(title=data["title"]).first()
    if not scholarship:
        scholarship = Scholarship(
            title=data["title"],
            description=f"{data['title']} supports students based on academic need, financial need, and retention risk.",
            provider=data["provider"],
            amount=data["amount"],
            application_deadline=datetime.utcnow() + timedelta(days=30),
            created_by=admin_id,
        )
        db.session.add(scholarship)
        db.session.flush()

    scholarship.provider = data["provider"]
    scholarship.amount = data["amount"]
    scholarship.currency = "INR"
    scholarship.payment_frequency = "One-time"
    scholarship.min_gpa = data["min_gpa"]
    scholarship.max_income = data["max_income"]
    scholarship.required_credits = 30
    scholarship.departments = json.dumps(data["departments"])
    scholarship.application_deadline = datetime.utcnow() + timedelta(days=30)
    scholarship.status = ScholarshipStatus.ACTIVE
    scholarship.ai_tags = data["tags"]
    scholarship.ai_popularity_score = 80
    scholarship.application_process = "Submit academic details, financial proof, and personal statement online."
    scholarship.required_documents = json.dumps(["ID Proof", "Marksheets", "Income Certificate"])
    return scholarship


def _ensure_application(student, scholarship, status, days_ago, success_probability):
    app = ScholarshipApplication.query.filter_by(
        student_id=student.id,
        scholarship_id=scholarship.id,
    ).first()
    if not app:
        app = ScholarshipApplication(
            student_id=student.id,
            scholarship_id=scholarship.id,
            application_date=datetime.utcnow() - timedelta(days=days_ago),
        )
        db.session.add(app)
    app.status = status
    app.gpa_at_application = student.gpa
    app.ai_eligibility_score = round(success_probability * 100, 1)
    app.ai_success_probability = success_probability
    app.personal_statement = "I need this scholarship to continue my academic progress."
    app.financial_justification = "Family income and education expenses require additional support."
    if status in {ApplicationStatus.APPROVED, ApplicationStatus.REJECTED}:
        app.review_date = datetime.utcnow() - timedelta(days=max(days_ago - 1, 0))
        app.review_comments = "Reviewed during demo data setup."
    return app


def _ensure_counselling_request(student, status, priority, topic, days_ago, counsellor=None):
    request_row = CounsellingRequest.query.filter_by(student_id=student.id, topic=topic).first()
    if not request_row:
        request_row = CounsellingRequest(
            student_id=student.id,
            user_id=student.user_id,
            topic=topic,
            request_date=datetime.utcnow() - timedelta(days=days_ago),
        )
        db.session.add(request_row)
    request_row.status = status
    request_row.priority = priority
    request_row.counselling_type = "academic" if "attendance" in topic.lower() else "personal"
    request_row.description = f"Student needs support for {topic.lower()}."
    request_row.preferred_date = datetime.utcnow() + timedelta(days=2)
    request_row.preferred_time = "11:00 AM"
    if counsellor and status in {CounsellingStatus.SCHEDULED, CounsellingStatus.COMPLETED}:
        request_row.assigned_counsellor_id = counsellor.id
        request_row.scheduled_date = datetime.utcnow() + timedelta(days=1)
    if status == CounsellingStatus.COMPLETED:
        request_row.session_notes = "Initial counselling completed and follow-up suggested."
        request_row.follow_up_required = True
        request_row.follow_up_date = datetime.utcnow() + timedelta(days=10)
    return request_row


def ensure_demo_data(total_students=80):
    admin = _ensure_user("admin@eduguard.edu", "admin", "admin", "admin123")
    faculty = _ensure_user("faculty@eduguard.edu", "faculty", "faculty", "faculty123")

    students = {row["student_id"]: _ensure_demo_student(row) for row in generated_student_rows(total_students)}
    scholarships = {
        row["title"]: _ensure_scholarship(row, admin.id)
        for row in DEMO_SCHOLARSHIPS
    }

    application_specs = [
        ("ST001", "Merit Excellence Grant", ApplicationStatus.APPROVED, 18, 0.92),
        ("ST002", "Need Based Support Fund", ApplicationStatus.PENDING, 8, 0.78),
        ("ST003", "Need Based Support Fund", ApplicationStatus.UNDER_REVIEW, 5, 0.61),
        ("ST004", "Attendance Improvement Aid", ApplicationStatus.PENDING, 2, 0.55),
        ("ST005", "Attendance Improvement Aid", ApplicationStatus.REJECTED, 16, 0.32),
        ("ST002", "Women in Technology Scholarship", ApplicationStatus.APPROVED, 24, 0.81),
    ]
    for student_id, title, status, days_ago, probability in application_specs:
        _ensure_application(students[student_id], scholarships[title], status, days_ago, probability)

    scholarship_cycle = list(scholarships.values())
    status_cycle = [
        ApplicationStatus.PENDING,
        ApplicationStatus.APPROVED,
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.REJECTED,
    ]
    for index, student in enumerate(students.values(), start=1):
        primary = scholarship_cycle[index % len(scholarship_cycle)]
        status = status_cycle[index % len(status_cycle)]
        risk_profile = student.risk_profile
        base_probability = 0.82
        if risk_profile and risk_profile.risk_level == "Critical":
            base_probability = 0.35
        elif risk_profile and risk_profile.risk_level == "High":
            base_probability = 0.52
        elif risk_profile and risk_profile.risk_level == "Medium":
            base_probability = 0.66
        _ensure_application(
            student,
            primary,
            status,
            days_ago=(index % 26) + 1,
            success_probability=min(0.95, base_probability + ((index % 5) * 0.02)),
        )
        if index % 4 == 0:
            secondary = scholarship_cycle[(index + 1) % len(scholarship_cycle)]
            _ensure_application(
                student,
                secondary,
                ApplicationStatus.PENDING if index % 8 == 0 else ApplicationStatus.APPROVED,
                days_ago=(index % 18) + 2,
                success_probability=min(0.9, base_probability + 0.08),
            )

    _ensure_counselling_request(
        students["ST003"],
        CounsellingStatus.REQUESTED,
        "urgent",
        "Low attendance and academic pressure",
        1,
        faculty,
    )
    _ensure_counselling_request(
        students["ST005"],
        CounsellingStatus.SCHEDULED,
        "high",
        "Financial and health support",
        3,
        faculty,
    )
    _ensure_counselling_request(
        students["ST004"],
        CounsellingStatus.COMPLETED,
        "medium",
        "Family pressure and confidence building",
        9,
        faculty,
    )

    for index, student in enumerate(students.values(), start=1):
        risk_profile = student.risk_profile
        if not risk_profile or risk_profile.risk_level not in {"High", "Critical"}:
            continue
        if index % 3 == 0:
            status = CounsellingStatus.REQUESTED
        elif index % 3 == 1:
            status = CounsellingStatus.SCHEDULED
        else:
            status = CounsellingStatus.COMPLETED
        _ensure_counselling_request(
            student,
            status,
            "urgent" if risk_profile.risk_level == "Critical" else "high",
            f"{risk_profile.risk_level} risk intervention",
            days_ago=(index % 12) + 1,
            counsellor=faculty,
        )

    for student in students.values():
        sync_student_risk_inputs(student)

    admin_notification = Notification.query.filter_by(
        user_id=admin.id,
        title="Demo data ready for EduGuard",
    ).first()
    if not admin_notification:
        db.session.add(
            Notification(
                user_id=admin.id,
                title="Demo data ready for EduGuard",
                message="Scholarships, applications, counselling requests, and risk profiles are available for demo.",
                notification_type="system",
                priority="medium",
                action_required=False,
            )
        )

    db.session.commit()
