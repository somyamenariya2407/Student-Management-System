from db import db
from datetime import date
from sqlalchemy import Enum
import enum

# ----------------- Attendance Status Enum -----------------
class AttendanceStatus(enum.Enum):
    A = "ABSENT"
    P = "PRESENT"


# ----------------- User Table (Admin & Faculty) -----------------
class User(db.Model):
    
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    branch = db.Column(db.String(100), nullable=True, default='NA')
    course = db.Column(db.String(100), nullable=True, default='NA')
    role = db.Column(db.String(50), nullable=False, default='Faculty')  # Admin or Faculty

    def __repr__(self):
        return f"<User {self.name} - {self.role}>"


# ----------------- Student Table -----------------
class Student(db.Model):
    
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False)

   
    def __repr__(self):
        return f"<Student {self.name} - Sem {self.semester}>"


# ----------------- Subject Table -----------------
class Subject(db.Model):
    
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Subject {self.name} - Sem {self.semester}>"


# ----------------- Faculty-Subject Mapping Table -----------------
class FacultySubject(db.Model):
    
    
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    faculty = db.relationship('User', backref=db.backref('faculty_subjects', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('faculty_subjects', lazy=True))

    def __repr__(self):
        return f"<FacultySubject Faculty={self.faculty_id} Subject={self.subject_id}>"


# ----------------- Attendance Table -----------------
class Attendance(db.Model):
   
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    status = db.Column(db.Enum(AttendanceStatus), nullable=False)

    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('attendances', lazy=True))

    def __repr__(self):
        return f"<Attendance Student={self.student_id} Subject={self.subject_id} Date={self.date}>"


# ----------------- Marks Table -----------------
class Marks(db.Model):
    
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Float, nullable=False)
    grade= db.Column(db.String(5), nullable=True)
    
    student = db.relationship('Student', backref=db.backref('marks', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('marks', lazy=True))

    def __repr__(self):
        return f"<Marks Student={self.student_id} Subject={self.subject_id} {self.marks_obtained}/{self.total_marks}>"


