"""
EduGuard - Comprehensive Database Seed Script
50 Indian students | 60-day attendance | Full risk data
Run: python seed_database.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from models import db, User, Student, Attendance, RiskProfile, Counselling, MentorAssignment, Alert
from datetime import datetime, date, timedelta
import random
random.seed(42)

STUDENTS = [
    # sid, fname, lname, dept, year, sem, gpa, behavior, att_pct, fin, fam, health, social, mental, parent_name
    # CRITICAL RISK
    ("ST3001","Rohit",   "Verma",     "Computer Science",2,3,4.1,2.5,48,True, True, True, True, 2.0,"Suresh Verma"),
    ("ST3002","Neha",    "Sharma",    "Engineering",     3,5,3.8,2.0,52,True, True, False,True, 3.0,"Ramesh Sharma"),
    ("ST3003","Arjun",   "Yadav",     "Commerce",        4,7,4.5,3.0,50,False,True, True, True, 2.5,"Ramkumar Yadav"),
    # HIGH RISK
    ("ST3004","Sneha",   "Reddy",     "Arts",            3,5,5.2,4.0,63,True, False,True, False,4.5,"Vijay Reddy"),
    ("ST3005","Karan",   "Malhotra",  "Science",         2,3,5.5,3.5,58,True, True, False,False,4.0,"Anil Malhotra"),
    ("ST3006","Divya",   "Nair",      "Computer Science",4,7,4.9,3.0,61,False,True, False,True, 3.5,"Rajan Nair"),
    ("ST3007","Manish",  "Gupta",     "Engineering",     1,2,5.8,4.5,60,True, False,False,True, 5.0,"Deepak Gupta"),
    ("ST3008","Priya",   "Singh",     "Business",        3,5,5.1,3.8,64,False,True, True, False,4.0,"Harpal Singh"),
    # MEDIUM RISK
    ("ST3009","Rahul",   "Patel",     "Science",         2,3,6.8,5.5,72,False,True, False,False,6.0,"Sunil Patel"),
    ("ST3010","Ananya",  "Joshi",     "Commerce",        3,5,7.0,6.0,75,False,False,True, False,6.5,"Mahesh Joshi"),
    ("ST3011","Vikash",  "Tiwari",    "Arts",            2,3,6.5,5.0,70,True, False,False,False,7.0,"Gopal Tiwari"),
    ("ST3012","Sonia",   "Mehta",     "Computer Science",4,7,6.9,6.5,74,False,True, False,False,6.0,"Haresh Mehta"),
    ("ST3013","Aditya",  "Kumar",     "Engineering",     1,2,7.2,6.0,71,False,False,False,True, 7.5,"Anil Kumar"),
    ("ST3014","Pooja",   "Mishra",    "Business",        3,5,6.3,5.5,73,True, False,False,False,6.5,"Dinesh Mishra"),
    ("ST3015","Sumit",   "Pandey",    "Science",         2,3,7.1,6.5,78,False,False,True, False,7.0,"Ramesh Pandey"),
    ("ST3016","Nisha",   "Bose",      "Commerce",        4,7,6.7,5.8,76,False,False,False,False,6.8,"Subhash Bose"),
    ("ST3017","Gaurav",  "Sinha",     "Arts",            1,2,7.0,6.2,69,False,True, False,False,6.5,"Ravi Sinha"),
    ("ST3018","Komal",   "Shah",      "Computer Science",3,5,6.4,5.5,77,False,False,False,False,7.2,"Bharat Shah"),
    # LOW RISK
    ("ST3019","Aakash",  "Sharma",    "Engineering",     2,3,8.5,8.5,92,False,False,False,False,9.0,"Vijay Sharma"),
    ("ST3020","Meera",   "Iyer",      "Science",         3,5,9.1,9.0,95,False,False,False,False,9.5,"Suresh Iyer"),
    ("ST3021","Ravi",    "Nair",      "Computer Science",4,7,8.8,8.8,93,False,False,False,False,9.0,"Mohan Nair"),
    ("ST3022","Shreya",  "Das",       "Arts",            1,2,8.2,8.0,88,False,False,False,False,8.5,"Subir Das"),
    ("ST3023","Tarun",   "Gupta",     "Business",        2,3,8.7,8.5,90,False,False,False,False,9.0,"Deepak Gupta"),
    ("ST3024","Anjali",  "Verma",     "Commerce",        3,5,9.3,9.5,97,False,False,False,False,10.0,"Suresh Verma"),
    ("ST3025","Saurabh", "Jain",      "Engineering",     4,7,8.9,9.0,94,False,False,False,False,9.2,"Rajesh Jain"),
    ("ST3026","Kavya",   "Reddy",     "Science",         1,2,8.4,8.2,89,False,False,False,False,8.8,"Ravi Reddy"),
    ("ST3027","Nikhil",  "Tiwari",    "Computer Science",2,3,9.0,9.2,96,False,False,False,False,9.5,"Gopal Tiwari"),
    ("ST3028","Preethi", "Krishnan",  "Arts",            3,5,8.6,8.5,91,False,False,False,False,9.0,"Rajan Krishnan"),
    ("ST3029","Abhishek","Malik",     "Business",        4,7,8.3,8.0,87,False,False,False,False,8.5,"Anil Malik"),
    ("ST3030","Ritika",  "Chauhan",   "Commerce",        1,2,8.9,8.8,93,False,False,False,False,9.2,"Sanjay Chauhan"),
    # MORE STUDENTS
    ("ST3031","Vishal",  "Agarwal",   "Computer Science",2,4,7.5,7.0,83,False,False,False,False,8.0,"Ramesh Agarwal"),
    ("ST3032","Pallavi", "Shukla",    "Engineering",     3,6,7.8,7.5,85,False,False,False,False,8.2,"Suresh Shukla"),
    ("ST3033","Harsh",   "Tripathi",  "Science",         4,8,7.2,6.8,80,False,True, False,False,7.5,"Anil Tripathi"),
    ("ST3034","Simran",  "Kaur",      "Arts",            1,1,7.6,7.2,84,False,False,False,False,8.0,"Gurpreet Kaur"),
    ("ST3035","Akash",   "Yadav",     "Business",        2,3,6.0,5.2,68,True, False,False,True, 6.0,"Ramkumar Yadav"),
    ("ST3036","Tanvi",   "Patil",     "Commerce",        3,5,8.1,8.0,86,False,False,False,False,8.5,"Sunil Patil"),
    ("ST3037","Kartik",  "Bansal",    "Computer Science",4,7,7.9,7.8,87,False,False,False,False,8.2,"Deepak Bansal"),
    ("ST3038","Ishita",  "Saxena",    "Engineering",     2,3,5.4,4.5,65,True, True, False,False,5.0,"Rajesh Saxena"),
    ("ST3039","Mohit",   "Rathore",   "Science",         3,5,8.3,8.2,89,False,False,False,False,8.8,"Bharat Rathore"),
    ("ST3040","Deepika", "Pillai",    "Arts",            1,2,7.4,7.0,82,False,False,True, False,7.8,"Suresh Pillai"),
    ("ST3041","Yash",    "Kulkarni",  "Business",        2,4,9.2,9.0,95,False,False,False,False,9.5,"Vijay Kulkarni"),
    ("ST3042","Swati",   "Dubey",     "Commerce",        3,6,6.6,6.0,74,False,False,False,True, 6.5,"Ramesh Dubey"),
    ("ST3043","Pranav",  "Mathur",    "Computer Science",4,8,7.7,7.5,85,False,False,False,False,8.0,"Anil Mathur"),
    ("ST3044","Riddhi",  "Srivastava","Engineering",     1,2,8.0,7.8,86,False,False,False,False,8.3,"Gopal Srivastava"),
    ("ST3045","Chirag",  "Vyas",      "Science",         2,3,5.7,5.0,67,True, False,True, False,5.5,"Suresh Vyas"),
    ("ST3046","Natasha", "Ahuja",     "Arts",            3,5,8.5,8.3,90,False,False,False,False,9.0,"Harish Ahuja"),
    ("ST3047","Varun",   "Kapoor",    "Business",        4,7,7.3,7.0,81,False,True, False,False,7.5,"Anil Kapoor"),
    ("ST3048","Shreya",  "Menon",     "Commerce",        1,1,9.4,9.5,98,False,False,False,False,10.0,"Rajan Menon"),
    ("ST3049","Parth",   "Thakur",    "Computer Science",2,3,4.3,2.8,55,True, True, True, False,3.5,"Vijay Thakur"),
    ("ST3050","Alisha",  "Fernandes", "Engineering",     3,5,8.7,8.6,91,False,False,False,False,9.1,"Mario Fernandes"),
]

COURSES = ["Mathematics","Physics","Programming","English","Data Structures",
           "Chemistry","Economics","Digital Electronics","DBMS","Operating Systems"]


def main():
    app = create_app()
    with app.app_context():
        print("\n" + "="*55)
        print("  EduGuard Comprehensive Database Seeding")
        print("  50 Students | 60-day Attendance | Full Risk Data")
        print("="*55)

        # Step 1: Clear
        print("\nStep 1: Purana data clear kar rahe hain...")
        Alert.query.delete()
        Counselling.query.delete()
        MentorAssignment.query.delete()
        RiskProfile.query.delete()
        Attendance.query.delete()
        Student.query.delete()
        User.query.delete()
        db.session.commit()
        print("  Done")

        # Step 2: Users
        print("\nStep 2: Users bana rahe hain...")
        for uname, email, pwd, role in [
            ("admin",     "admin@eduguard.edu",     "admin123",   "admin"),
            ("dr_sharma", "dr.sharma@eduguard.edu", "faculty123", "faculty"),
            ("dr_patel",  "dr.patel@eduguard.edu",  "faculty123", "faculty"),
            ("ms_iyer",   "ms.iyer@eduguard.edu",   "faculty123", "faculty"),
            ("counselor", "counselor@eduguard.edu", "counsel123", "faculty"),
        ]:
            u = User(username=uname, email=email, role=role)
            u.set_password(pwd)
            db.session.add(u)
            print(f"  + {role}: {email}")
        db.session.commit()

        # Step 3: Students
        print("\nStep 3: 50 students bana rahe hain...")
        phones = set()
        student_objs = []
        for row in STUDENTS:
            sid,fname,lname,dept,year,sem,gpa,bscore,att,fin,fam,health,social,mental,pname = row
            phone = f"98{random.randint(10000000,99999999)}"
            while phone in phones: phone = f"98{random.randint(10000000,99999999)}"
            phones.add(phone)
            s = Student(
                student_id=sid, first_name=fname, last_name=lname,
                email=f"{fname.lower()}.{lname.lower()}@eduguard.edu",
                department=dept, year=year, semester=sem, gpa=gpa,
                behavior_score=bscore,
                enrollment_date=date.today()-timedelta(days=year*365+random.randint(0,60)),
                credits_completed=sem*18,
                parent_name=pname,
                parent_email=f"{pname.split()[0].lower()}@gmail.com",
                parent_phone=phone
            )
            db.session.add(s)
            student_objs.append((s, row))
            print(f"  + {sid} {fname} {lname} | {dept} | GPA:{gpa} | Attendance:{att}%")
        db.session.commit()

        # Step 4: Attendance
        print("\nStep 4: Attendance records bana rahe hain (60 din)...")
        total_att = 0
        for (s, row) in student_objs:
            att_pct = row[8]
            for days_ago in range(60):
                att_date = date.today() - timedelta(days=days_ago)
                if att_date.weekday() >= 5: continue
                for course in random.sample(COURSES, 5):
                    r = random.randint(1,100)
                    if r <= att_pct: status = "Present"
                    elif r <= att_pct+5: status = "Late"
                    else: status = "Absent"
                    db.session.add(Attendance(student_id=s.id, date=att_date, status=status, course=course))
                    total_att += 1
        db.session.commit()
        print(f"  Total: {total_att} records")

        # Step 5: Risk Profiles
        print("\nStep 5: Risk profiles calculate kar rahe hain...")
        for (s, row) in student_objs:
            sid,fname,lname,dept,year,sem,gpa,bscore,att_pct,fin,fam,health,social,mental,pname = row
            recs = Attendance.query.filter_by(student_id=s.id).all()
            if recs:
                present = sum(1 for a in recs if a.status=="Present")
                late    = sum(1 for a in recs if a.status=="Late")
                att_rate = round(((present + late*0.5)/len(recs))*100, 1)
            else:
                att_rate = float(att_pct)
            rp = RiskProfile(
                student_id=s.id,
                attendance_rate=att_rate,
                academic_performance=round(gpa*10,1),
                financial_issues=fin, family_problems=fam,
                health_issues=health, social_isolation=social,
                mental_wellbeing_score=float(mental)
            )
            rp.update_risk_score()
            db.session.add(rp)
            print(f"  {sid}: {rp.risk_level} (score={rp.risk_score:.1f}, att={att_rate}%)")
        db.session.commit()

        # Step 6: Counselling + Alerts + Mentors
        print("\nStep 6: Counselling, Alerts, Mentor assignments...")
        faculty_list = User.query.filter_by(role="faculty").all()
        c_cnt = a_cnt = m_cnt = 0
        for (s, _) in student_objs:
            rp = RiskProfile.query.filter_by(student_id=s.id).first()
            if not rp: continue
            lvl = rp.risk_level
            if lvl in ["Medium","High","Critical"]:
                sessions = 2 if lvl=="Critical" else 1
                for i in range(sessions):
                    db.session.add(Counselling(
                        student_id=s.id, counsellor_id=faculty_list[0].id,
                        session_date=datetime.now()-timedelta(days=random.randint(1,20)+i*7),
                        session_type="Individual" if lvl!="Medium" else "Group",
                        status=random.choice(["Scheduled","Completed"]),
                        notes=f"Risk reasons: {rp.risk_reasons}",
                        follow_up_required=(lvl in ["High","Critical"])
                    ))
                    c_cnt += 1
            if lvl in ["High","Critical"]:
                db.session.add(Alert(
                    student_id=s.id, alert_type="Risk Level", severity=lvl,
                    title=f"{lvl} Dropout Risk — {s.first_name} {s.last_name}",
                    description=f"Score:{rp.risk_score:.1f} | Att:{rp.attendance_rate}% | Acad:{rp.academic_performance}% | {rp.risk_reasons}",
                    status="Active",
                    created_at=datetime.now()-timedelta(days=random.randint(1,10))
                ))
                a_cnt += 1
                db.session.add(MentorAssignment(
                    student_id=s.id, mentor_id=random.choice(faculty_list).id,
                    assignment_date=datetime.now()-timedelta(days=random.randint(1,15)),
                    status="Active", notes=f"Assigned due to {lvl} dropout risk."
                ))
                m_cnt += 1
        db.session.commit()
        print(f"  Counselling:{c_cnt}  Alerts:{a_cnt}  Mentors:{m_cnt}")

        # Summary
        print("\n" + "="*55)
        print("  FINAL SUMMARY")
        print("="*55)
        print(f"  Users:              {User.query.count()}")
        print(f"  Students:           {Student.query.count()}")
        print(f"  Attendance records: {Attendance.query.count()}")
        print(f"  Risk Profiles:      {RiskProfile.query.count()}")
        print(f"  Counselling:        {Counselling.query.count()}")
        print(f"  Mentor Assignments: {MentorAssignment.query.count()}")
        print(f"  Alerts:             {Alert.query.count()}")
        print("\n  Risk Distribution:")
        for lvl, em in [("Low","Low"),("Medium","Medium"),("High","High"),("Critical","Critical")]:
            c = RiskProfile.query.filter_by(risk_level=lvl).count()
            print(f"    {em:8}: {c}")
        print("\n" + "="*55)
        print("  LOGIN CREDENTIALS")
        print("="*55)
        print("  Admin:     admin@eduguard.edu      / admin123")
        print("  Faculty:   dr.sharma@eduguard.edu  / faculty123")
        print("  Counselor: counselor@eduguard.edu  / counsel123")
        print("="*55)
        print("\n  Done! Ab chalao: python run.py\n")


if __name__ == "__main__":
    main()
