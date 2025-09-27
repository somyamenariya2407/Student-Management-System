from flask import Blueprint,render_template,redirect,request,url_for,session,flash
from models.models import db,User,Student,Attendance,Marks,Subject,FacultySubject,AttendanceStatus
from datetime import datetime,date
from werkzeug.security import generate_password_hash

faculty_bp = Blueprint('faculty', __name__,url_prefix="/faculty")


@faculty_bp.route('/view_details')
def view_details():
    if 'user_id' not in session or session.get('role') != 'faculty':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    if 'email' not in session:
        flash("Unauthorized Access", "danger")
        return redirect(url_for('auth.login'))

    email = session['email']
    faculty = User.query.filter_by(email=email).first()
    
    return render_template("faculty/view_details.html",faculty=faculty)


@faculty_bp.route('/dashboard')

def faculty_dashboard():
    if 'user_id' not in session or session.get('role') != 'faculty':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    if 'email' not in session:
        flash("Unauthorized Access", "danger")
        return redirect(url_for('auth.login'))

    email = session['email']

    faculty = User.query.filter_by(email=email).first()
    if not faculty:
        flash("Faculty not found.", "danger")
        return redirect(url_for('auth.login'))
    

    assigned_courses = []
    if faculty.course:
        assigned_courses = [course.strip() for course in faculty.course.split(",")]
    
    

    return render_template("faculty/faculty_dashboard.html", faculty=faculty, assigned_courses=assigned_courses)

#-----------------------------------ATTENDANCE-----------------------------------

@faculty_bp.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'user_id' not in session or session.get('role') != 'faculty':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    
    if 'email' not in session:
        flash("Unauthorized Access", "danger")
        return redirect(url_for('auth.login'))

    email = session['email']
    faculty = User.query.filter_by(email=email).first()

    if not faculty:
        flash("Faculty not found.", "danger")
        return redirect(url_for('auth.login'))

    # Faculty ke assigned courses nikalna
    assigned_courses = []
    if faculty.course:
        assigned_courses = [course.strip() for course in faculty.course.split(",")]

    # Jab koi course pe click kare tab students ka list dikhaye
    selected_course = request.args.get('course')
    students = []
    attendance_data={}
    today_date=date.today().strftime("%Y-%m-%d")
    

    subject = None

    if selected_course:
        subject = Subject.query.filter_by(name=selected_course).first()
        if subject:
            students = Student.query.filter_by(semester=subject.semester).all()

            for student in students:
                total_classes = Attendance.query.filter_by(student_id=student.id, subject_id=subject.id).count()
                present_count = Attendance.query.filter_by(student_id=student.id, subject_id=subject.id, status="P").count()
                percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
                attendance_data[student.id] = round(percentage,2)


    if request.method == 'POST' :
        date_str=request.form.get('attendance_date') or today_date
        attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        if attendance_date != date.today():
            flash("You can only mark attendance for Today's date.", "danger")
            return redirect(url_for('faculty.attendance', course=selected_course))

        present_students=request.form.getlist("present_students")

        for student in students:

            status = "P" if str(student.id) in present_students else "A"

            existing_record = Attendance.query.filter_by(student_id=student.id, subject_id=subject.id, date=attendance_date).first()

            if existing_record:
                existing_record.status = status
            
            else:

                new_attendance = Attendance(
                    student_id=student.id,
                    subject_id=subject.id,date=attendance_date,
                    status=status
                )
                db.session.add(new_attendance)
        db.session.commit()
        flash("Attendance saved successfully!", "success")
        return redirect(url_for('faculty.attendance'))

    return render_template("faculty/attendance.html",faculty=faculty,
                           assigned_courses=assigned_courses,
                           selected_course=selected_course,
                           students=students,current_date=today_date,attendance_data=attendance_data)

#-----------------------------------VIEW ATTENDANCE-------------------------------

@faculty_bp.route('/view_attendance', methods=['GET', 'POST'])
def view_attendance():
    if 'user_id' not in session or session.get('role') != 'faculty':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    
    if 'email' not in session:
        flash("Unauthorized Access", "danger")
        return redirect(url_for('auth.login'))

    email = session['email']
    faculty = User.query.filter_by(email=email).first()
    if not faculty:
        flash("Faculty not found.", "danger")
        return redirect(url_for('auth.login'))

    # Faculty ke assigned courses
    assigned_courses = []
    if faculty.course:
        assigned_courses = [course.strip() for course in faculty.course.split(",")]

    selected_course = None
    selected_date = None
    selected_status = None
    
    attendance_records = []
    attendance_summary= []

    if request.method == 'POST':
        selected_course = request.form.get('course')
        selected_date = request.form.get('attendance_date')
        selected_status = request.form.get('status_filter')

        if selected_course and selected_date:
            subject = Subject.query.filter_by(name=selected_course).first()
            if subject:
                try:
                    date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
                    query= db.session.query(Student, Attendance).join(
                        Attendance, Student.id == Attendance.student_id
                    ).filter(Attendance.subject_id == subject.id,Attendance.date == date_obj)
                

                    if selected_status and selected_status != "ALL":
                        query=query.filter(Attendance.status == selected_status)

                    attendance_records = query.all()

                # Attendance Summary Calculation
                    summary_query = db.session.query(
                            Student.id,
                            Student.name,
                            Student.roll_number,
                            db.func.count(Attendance.id).label("total_days"),
                            db.func.sum(db.case((Attendance.status == "P", 1), else_=0)).label("present_days")
                        ).join(Attendance, Student.id == Attendance.student_id
                        ).filter(
                            Attendance.subject_id == subject.id,
                            Attendance.date <= date_obj
                        ).group_by(Student.id).all()

                    attendance_summary=[{
                            "name": row.name,
                            "roll_number": row.roll_number,
                            "present_days": row.present_days if row.present_days else 0,
                            "total_days": row.total_days,
                            "percentage": round((row.present_days / row.total_days) * 100, 2) if row.total_days > 0 else 0


                    }
                    for row in summary_query
                    ]
                except Exception as e:
                    flash("Error processing the date. Please use YYYY-MM-DD format.", "danger")


                        

    return render_template("faculty/view_attendance.html",faculty=faculty,
                           assigned_courses=assigned_courses,
                           selected_course=selected_course,
                           selected_date=selected_date,selected_status=selected_status,
                           attendance_summary=attendance_summary,
                           attendance_records=attendance_records)


@faculty_bp.route('/attendance_summary', methods=['GET', 'POST'])
def attendance_summary():
    if 'user_id' not in session or session.get('role') != 'faculty':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    if 'email' not in session:
        flash("Unauthorized Access", "danger")
        return redirect(url_for('auth.login'))

    email = session['email']
    faculty = User.query.filter_by(email=email).first()
    if not faculty:
        flash("Faculty not found.", "danger")
        return redirect(url_for('auth.login'))

    assigned_courses = []
    if faculty.course:
        assigned_courses = [course.strip() for course in faculty.course.split(",")]

    selected_course = None
    selected_date = None
    attendance_summary = []

    if request.method == 'POST':
        selected_course = request.form.get('course')
        selected_date = request.form.get('attendance_date')

        if selected_course and selected_date:
            subject = Subject.query.filter_by(name=selected_course).first()
            if subject:
                try:
                    date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

                    summary_query = db.session.query(
                        Student.id,
                        Student.name,
                        Student.roll_number,
                        db.func.count(Attendance.id).label("total_days"),
                        db.func.sum(db.case((Attendance.status == "P", 1), else_=0)).label("present_days")
                    ).join(Attendance, Student.id == Attendance.student_id
                    ).filter(
                        Attendance.subject_id == subject.id,
                        Attendance.date <= date_obj
                    ).group_by(Student.id).all()

                    attendance_summary = [{
                        "name": row.name,
                        "roll_number": row.roll_number,
                        "present_days": row.present_days if row.present_days else 0,
                        "total_days": row.total_days,
                        "percentage": round((row.present_days / row.total_days) * 100, 2) if row.total_days > 0 else 0
                    } for row in summary_query]

                except Exception as e:
                    flash(f"Error: {str(e)}", "danger")

    return render_template("faculty/attendance_summary.html",
                           faculty=faculty,
                           assigned_courses=assigned_courses,
                           selected_course=selected_course,
                           selected_date=selected_date,
                           attendance_summary=attendance_summary)

#--------------------------MARKS---------------------------------

@faculty_bp.route('/marks', methods=['GET', 'POST'])
def marks():
    if 'user_id' not in session or session.get('role') != 'faculty':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))


    if 'email' not in session:
        flash("Unauthorized Access", "danger")
        return redirect(url_for('auth.login'))

    email = session['email']
    faculty = User.query.filter_by(email=email).first()

    if not faculty:
        flash("Faculty not found.", "danger")
        return redirect(url_for('auth.login'))

    # 2. Assigned courses list
    assigned_courses = []
    if faculty.course:
        assigned_courses = [course.strip() for course in faculty.course.split(",")]

    # 3. Course selection
    selected_course = request.args.get('course')
    students = []
    subject = None
    total_marks=100  # Default total marks

    if selected_course:
        subject = Subject.query.filter_by(name=selected_course).first()
        if subject:
            students = Student.query.filter_by(semester=subject.semester).all()


    def calculate_grade(marks, total):
        percentage = (marks / total) * 100
        if percentage >= 90:
            return "A++"
        elif percentage >= 85:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 75:
            return "B+"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C+"
        elif percentage >= 50:
            return "C"
        elif percentage >= 40:
            return "D"
        else:
            return "F"

     # 4. On form submit -> Save Marks
    if request.method == 'POST':
        total_marks = request.form.get('total_marks') or 100
        for student in students:
            marks_value = request.form.get(f"marks_{student.id}")
            if marks_value:
                marks_value = float(marks_value)
                grade = calculate_grade(marks_value, total_marks)

                existing_mark = Marks.query.filter_by(student_id=student.id, subject_id=subject.id).first()
                
                if existing_mark:
                    existing_mark.marks_obtained = marks_value
                    existing_mark.total_marks = float(total_marks)
                    existing_mark.grade = grade
                
                else:
                    new_mark = Marks(
                        student_id=student.id,
                        subject_id=subject.id,
                        marks_obtained=float(marks_value),
                        total_marks=float(total_marks),
                        grade=grade
                    )
                    db.session.add(new_mark)
        db.session.commit()
        flash("Marks saved successfully!", "success")
        return redirect(url_for('faculty.marks'))

    marks_dict = {}
    if subject:
        marks_records = Marks.query.filter_by(subject_id=subject.id).all()
        for record in marks_records:
            marks_dict[record.student_id] = record

    return render_template("faculty/marks.html",faculty=faculty,
                           assigned_courses=assigned_courses,
                           selected_course=selected_course,
                           students=students,total_marks=total_marks,marks_dict=marks_dict
                           )

@faculty_bp.route('/view_marks', methods=['GET'])
def view_marks():
    if 'user_id' not in session or session.get('role') != 'faculty':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    
    if 'email' not in session:
        flash("Unauthorized Access", "danger")
        return redirect(url_for('auth.login'))

    email = session['email']
    faculty = User.query.filter_by(email=email).first()

    if not faculty:
        flash("Faculty not found.", "danger")
        return redirect(url_for('auth.login'))

    # Assigned courses list
    assigned_courses = []
    if faculty.course:
        assigned_courses = [course.strip() for course in faculty.course.split(",")]

    # Course selection
    selected_course = request.args.get('course')
    grade_filter= request.args.get('grade')
    min_marks= request.args.get('min_marks')
    max_marks=request.args.get('max_marks')

    marks_data = []
    subject = None

    if selected_course:
        subject = Subject.query.filter_by(name=selected_course).first()
        if subject:
             # Student + Marks join query
            query = db.session.query(Student, Marks).join(
                Marks, Student.id == Marks.student_id
            ).filter(Marks.subject_id == subject.id)

            if grade_filter and grade_filter!="All":
                query=query.filter(Marks.grade==grade_filter)

            if min_marks:
                query=query.filter(Marks.marks_obtained>= float(min_marks))

            if max_marks:
                query=query.filter(Marks.marks_obtained<=float(max_marks))


            marks_data=query.all()

    return render_template("faculty/view_marks.html",faculty=faculty,
                           assigned_courses=assigned_courses,
                           selected_course=selected_course,
                           marks_data=marks_data,grade_filter=grade_filter,min_marks=min_marks,max_marks=max_marks)



@faculty_bp.route('/marksheet_select', methods=['GET'])
def marksheet_select():
    if 'user_id' not in session or session.get('role') != 'faculty':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    
    if 'email' not in session:
        flash("Unauthorized Access", "danger")
        return redirect(url_for('auth.login'))

    email = session['email']
    faculty = User.query.filter_by(email=email).first()

    if not faculty:
        flash("Faculty not found.", "danger")
        return redirect(url_for('auth.login'))

    # Assigned courses se unique semesters nikalna
    assigned_courses = []
    if faculty.course:
        assigned_courses = [course.strip() for course in faculty.course.split(",")]

    semesters = list(set(
        Subject.query.filter(Subject.name.in_(assigned_courses))
        .with_entities(Subject.semester).all()
    ))
    semesters = [s[0] for s in semesters]  # Flatten tuple list

    selected_semester = request.args.get('semester')
    students = []

    # Agar semester select hua to student list laao
    if selected_semester:
        students = Student.query.filter_by(semester=selected_semester).all()

    return render_template("faculty/marksheet_select.html",faculty=faculty,
                           semesters=semesters,
                           selected_sem=selected_semester,
                           students_list=students)


@faculty_bp.route('/marksheet', methods=['GET'])
def marksheet():
    if 'user_id' not in session or session.get('role') != 'faculty':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    email = session['email']
    faculty = User.query.filter_by(email=email).first()

    if not faculty:
        flash("Faculty not found.", "danger")
        return redirect(url_for('auth.login'))


    student_id = request.args.get('student_id')

    if not student_id:
        flash("Student not found!", "danger")
        return redirect(url_for('faculty.marksheet_select'))

    student = Student.query.get(student_id)
    if not student:
        flash("Student not found!", "danger")
        return redirect(url_for('faculty.marksheet_select'))

    subjects = Subject.query.filter_by(semester=student.semester).all()

    marksheet_data = []
    total_marks = 0
    obtained_marks = 0

    # Marks data collect karna
    for subject in subjects:
        marks_record = Marks.query.filter_by(student_id=student.id, subject_id=subject.id).first()
        if marks_record:
            marksheet_data.append({
                "subject": subject.name,
                "code": f"CS{subject.id}",
                "marks": marks_record.marks_obtained,
                "total": marks_record.total_marks,
                "grade": marks_record.grade
            })
            total_marks += marks_record.total_marks
            obtained_marks += marks_record.marks_obtained

    # SGPA Calculation
    sgpa = round((obtained_marks / total_marks) * 10, 2) if total_marks > 0 else 0

    return render_template("faculty/marksheet.html",faculty=faculty,
                           student=student,
                           marksheet_data=marksheet_data,
                           sgpa=sgpa,
                           total_marks=total_marks,
                           obtained_marks=obtained_marks)

@faculty_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    admin=User.query.get(session['user_id'])
    return render_template("faculty/profile.html",admin=admin)


 

