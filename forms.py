from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, FloatField, DateField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = StringField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=64, message='Username must be between 3 and 64 characters')
    ])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[
        ('admin', 'Administrator'),
        ('faculty', 'Faculty'),
        ('student', 'Student')
    ], validators=[DataRequired()])

class StudentForm(FlaskForm):
    student_id = StringField('Student ID', validators=[
        DataRequired(),
        Length(min=3, max=20, message='Student ID must be between 3 and 20 characters')
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters')
    ])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    semester = IntegerField('Semester', validators=[
        DataRequired(),
        NumberRange(min=1, max=12, message='Semester must be between 1 and 12')
    ])

class InterventionForm(FlaskForm):
    type = SelectField('Intervention Type', choices=[
        ('Counseling', 'Counseling'),
        ('Parent Meeting', 'Parent Meeting'),
        ('Remedial Class', 'Remedial Class'),
        ('Academic Support', 'Academic Support'),
        ('Personal Issue', 'Personal Issue')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[
        DataRequired(),
        Length(min=10, max=1000, message='Notes must be between 10 and 1000 characters')
    ])

class AcademicRecordForm(FlaskForm):
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(min=2, max=50, message='Subject must be between 2 and 50 characters')
    ])
    score = FloatField('Score', validators=[
        DataRequired(),
        NumberRange(min=0, max=1000, message='Score must be between 0 and 1000')
    ])
    max_score = FloatField('Max Score', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000, message='Max score must be between 1 and 1000')
    ])
    exam_type = SelectField('Exam Type', choices=[
        ('Quiz', 'Quiz'),
        ('Midterm', 'Midterm'),
        ('Final', 'Final'),
        ('Assignment', 'Assignment'),
        ('Project', 'Project')
    ], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])

class AttendanceForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused')
    ], validators=[DataRequired()])
