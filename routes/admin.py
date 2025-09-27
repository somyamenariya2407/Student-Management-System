from flask import Blueprint,render_template,redirect,request,url_for,session,flash
from models.models import db,User,Student,Attendance,Marks,Subject
from datetime import datetime
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__,url_prefix="/admin")


def createadmin():
    admin_user = User.query.filter_by(role='admin').first()

    if not admin_user:
        hashed_pass= generate_password_hash('admin@123')
        admin = User(email='admin24@gmail.com',password=hashed_pass,name='Admin',role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin Created")
    else:
        print("Admin Already Exists")


@admin_bp.route('/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    total_students = Student.query.count()
    total_faculties = User.query.filter_by(role='faculty').count()
    total_courses = Subject.query.count()

    return render_template('/admin/admin_dashboard.html', total_students=total_students, total_faculties=total_faculties, total_courses=total_courses)


@admin_bp.route('/manage_faculty')
def manage_faculty():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    return render_template('admin/faculty/manage_faculty.html')

# Faculty List
@admin_bp.route('/view_faculty')
def view_faculty():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    faculties = User.query.filter_by(role='faculty').all()
    return render_template('admin/faculty/view_faculty.html', faculties=faculties)

# Faculty Details
@admin_bp.route('/faculty_deatils/<int:faculty_id>')
def faculty_details(faculty_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    

    faculty = User.query.get_or_404(faculty_id)
    return render_template('admin/faculty/faculty_details.html', faculty=faculty)

# ---------------------------Add Faculty-----------------------

@admin_bp.route('/add_faculty', methods=['GET', 'POST'])
def add_faculty():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    semesters=sorted([s[0] for s in db.session.query(Subject.semester).distinct().all()])
    all_subjects=Subject.query.all()

    assigned_courses = []
    faculties = User.query.filter_by(role='faculty').all()
    for fac in faculties:
        if fac.course:
            assigned_courses.extend(fac.course.split(","))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        branch = request.form.get('branch')
        selected_courses = request.form.getlist('course')  # Get multiple courses\\

        if not name or not email or not password or not branch:
            flash("All fields are required!", "danger")
            return redirect(url_for('admin.add_faculty'))

        if not selected_courses:
            flash("Please select at least one course!", "danger")
            return redirect(url_for('admin.add_faculty'))

        for c in selected_courses:
            if c in assigned_courses:
                flash(f"Course {c} is already assigned to another faculty.", "danger")
                return redirect(url_for('admin.add_faculty'))
            


        courses_str = ",".join(selected_courses)  # Convert list to string

        # check agar faculty pehle se exist to nahi hai
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Faculty with this email already exists!", "danger")
            return redirect(url_for('admin.view_faculty'))

        hashed_pass = generate_password_hash(password)
        new_faculty = User(email=email, password=hashed_pass,name=name,branch=branch,course=courses_str, role='faculty')
        db.session.add(new_faculty)
        db.session.commit()

        flash("Faculty added successfully!", "success")
        return redirect(url_for('admin.view_faculty'))

    return render_template('admin/faculty/add_faculty.html',semesters=semesters,all_subjects=all_subjects,assigned_courses=assigned_courses)


# ----------------------------Remove Faculty--------------------------

@admin_bp.route('/remove_faculty/<int:faculty_id>', methods=['POST'])
def remove_faculty(faculty_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    


    faculty = User.query.get_or_404(faculty_id)
    db.session.delete(faculty)
    db.session.commit()
    flash("Faculty removed successfully!", "success")
    return redirect(url_for('admin.view_faculty'))

# -------------------------------Edit Faculty--------------------------

@admin_bp.route('/edit_faculty/<int:faculty_id>', methods=['GET', 'POST'])
def edit_faculty(faculty_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    

    faculty = User.query.get_or_404(faculty_id)


    semesters=db.session.query(Subject.semester).distinct().all()
    semester_subjects={}
    for sem in semesters:
        sem_val=sem[0]
        semester_subjects[sem_val]=Subject.query.filter_by(semester=sem_val).all()


    assigned_courses_all=  []
    faculties = User.query.filter_by(role='faculty').all()
    for fac in faculties:
        if fac.course:
            assigned_courses_all.extend(fac.course.split(","))

    assigned_courses=faculty.course.split(",") if faculty.course else []

    if request.method == 'POST':
        faculty.name = request.form.get('name')
        faculty.email = request.form.get('email')
        faculty.branch = request.form.get('branch')
        faculty.course = request.form.getlist('course')  # multiple courses as list

        if not faculty.name or not faculty.email or not faculty.branch:
            flash("All fields are required!", "danger")
            return redirect(url_for('admin.edit_faculty', faculty_id=faculty_id))

        # Check if any of the selected courses are already assigned to another faculty
        # for c in faculty.course:
        #     if c in assigned_courses_all:
        #         flash(f"Course {c} is already assigned to another faculty.", "danger")
        #         return redirect(url_for('admin.edit_faculty', faculty_id=faculty.id))
        
        faculty.course = ",".join(faculty.course)  # convert list to string for DB

        password= request.form['password']
        if password:
            faculty.password = generate_password_hash(password)

        db.session.commit()
        flash("Faculty details updated successfully!", "success")
        return redirect(url_for('admin.view_faculty'))

    return render_template('admin/faculty/edit_faculty.html', faculty=faculty,semester_subjects=semester_subjects,assigned_courses=assigned_courses,assigned_courses_all=assigned_courses_all)


# -----------------STUDENT MANAGEMENT ROUTES-----------------

@admin_bp.route('/manage_student')
def manage_student():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    return render_template('admin/student/manage_student.html')

#-------------------ADD STUDENT------------------

@admin_bp.route('/add_student', methods=['GET', 'POST'])
def add_student():

    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    semesters = [
        (1, "1st Semester"), (2, "2nd Semester"), (3, "3rd Semester"),
        (4, "4th Semester"), (5, "5th Semester"), (6, "6th Semester"),
        (7, "7th Semester"), (8, "8th Semester")
    ]

    if request.method == 'POST':
        name = request.form.get('name')
        roll_number = request.form.get('roll_no')
        branch = request.form.get('branch')
        semester = int(request.form.get('semester'))

        if not name or not roll_number or not branch or not semester:
            flash("All fields are required!", "danger")
            return redirect(url_for('admin.add_student'))

        # Check if student with the same roll number already exists
        existing_student = Student.query.filter_by(roll_number=roll_number).first()
        if existing_student:
            flash("Student with this roll number already exists!", "danger")
            return redirect(url_for('admin.add_student'))

        new_student = Student(name=name, roll_number=roll_number, branch=branch, semester=semester)
        db.session.add(new_student)
        db.session.commit()

        flash("Student added successfully!", "success")
        return redirect(url_for('admin.manage_student'))
    return render_template('admin/student/add_student.html',semesters=semesters)
    
#--------------------------------VIEW STUDENT----------------------

@admin_bp.route('/view_student')
def view_student():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    students = Student.query.order_by(Student.semester).all()
    all_semesters = sorted({s.semester for s in students if s.semester is not None})
    selected_semester = request.args.get('semester',type=int)

    if selected_semester:
        
        students = [s for s in students if s.semester == selected_semester]
        semesters = {selected_semester: students}

    else:

        semesters = {}
        for s in students:
            sem=s.semester if s.semester is not None else 'N/A'
            if sem not in semesters:
                semesters[sem] = []
            semesters[sem].append(s)
    return render_template('admin/student/view_student.html', semesters=semesters,all_semesters=all_semesters,selected_semester=selected_semester)

#-------------------------REMOVE STUDENT-----------------------

@admin_bp.route('/remove_student/<int:student_id>', methods=['POST'])
def remove_student(student_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    

    student = Student.query.get_or_404(student_id)
    if student.attendances:
        flash("Cannot delete student with existing attendance records.", "danger")
        return redirect(url_for('admin.view_student'))
    
    db.session.delete(student)
    db.session.commit()
    flash("Student removed successfully!", "success")
    return redirect(url_for('admin.view_student'))

#--------------------------EDIT STUDENT----------------------

@admin_bp.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    

    student = Student.query.get_or_404(student_id)

    semesters = [
        (1, "1st Semester"), (2, "2nd Semester"), (3, "3rd Semester"),
        (4, "4th Semester"), (5, "5th Semester"), (6, "6th Semester"),
        (7, "7th Semester"), (8, "8th Semester")
    ]

    if request.method == 'POST':
        student.name = request.form.get('name')
        student.roll_number = request.form.get('roll_no')
        student.branch = request.form.get('branch')
        student.semester = int(request.form.get('semester'))

        if not student.name or not student.roll_number or not student.branch or not student.semester:
            flash("All fields are required!", "danger")
            return redirect(url_for('admin.edit_student', student_id=student_id))

        db.session.commit()
        flash("Student details updated successfully!", "success")
        return redirect(url_for('admin.view_student'))

    return render_template('admin/student/edit_student.html', student=student,semesters=semesters)

#---------------------------------STUDENT DETAILS-----------------------

@admin_bp.route('/student_details/<int:student_id>')
def student_details(student_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    student = Student.query.get_or_404(student_id)
    
    # attendances = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).all()
    # marks = Marks.query.filter_by(student_id=student.id).all()
    return render_template('admin/student/student_details.html', student=student)


#---------------------------SUBJECT MANAGEMENT ROUTES---------------------------
@admin_bp.route('/manage_subject')
def manage_subject():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    subject = Subject.query.order_by(Subject.semester.asc()).all()
    return render_template('admin/subject/manage_subject.html',subject=subject)

@admin_bp.route('/add_subject', methods=['POST'])

def add_subject():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
        
        
    name = request.form["name"]
    semester = request.form["semester"]
    branch = request.form["branch"]

    if not name or not semester or not branch:
        flash("All fields are required!", "danger")
        return redirect(url_for('admin.manage_subject'))
    
    
    # Check if subject already exists
    existing = Subject.query.filter_by(name=name, semester=semester, branch=branch).first()
    if existing:
        flash("Subject already exists!", "warning")
        return redirect(url_for("admin.manage_subject"))

    new_subject = Subject(name=name, semester=semester, branch=branch)
    db.session.add(new_subject)
    db.session.commit()
    flash("Subject added successfully!", "success")
    return redirect(url_for("admin.manage_subject"))

@admin_bp.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))


    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully!", "success")
    return redirect(url_for("admin.manage_subject"))

subjects_by_semester = {
    1: ["ENGINEERING MATHEMATICS-I","ENGINEERING CHEMISTRY","COMMUNICATION SKILLS","BASIC MECHANICAL ENGINEERING","BASIC CIVIL ENGINEERING","ENGINEERING CHEMISTRY LAB","LANGUAGE LAB","MANUFACTURING PRATICES WORKSHOP","BASIC CIVIL ENGINEERING LAB","COMPUTER AIDED ENGINEERING GRAPHICS","DISCIPLINE & EXTRA CURRICULAR ACTIVITIES"],
    2: ["ENGINEERING PHYSICS","HUMAN VALUES","PROGRAMMING FOR PROBLEM SOLVING","BASIC ELECTRICAL ENGINEERING","ENGINEERING PHYSICS LAB","HUMAN VALUES ACTIVITIES AND SPORTS","COMPUTER PROGRAMMING LAB","BASIC ELECTRICAL ENGINEERING LAB","COMPUTER AIDED MACHINE DRAWING","DISCIPLINE & EXTRA CURRICULAR ACTIVITIES","ENGINEERING MATHEMATICS-II"],
    3: ["ADVANCE ENGINEERING MATHEMATICS","TECHNICAL COMMUNICATION","DIGITAL ELECTRONICS","DATA STRUCTURES AND ALGORITHMS","OBJECT ORIENTED PROGRAMMING","SOFTWARE ENGINEERING","DATA STRUCTURES AND ALGORITHMS LAB","OBJECT ORIENTED PROGRAMMING LAB","SOFTWARE ENGINEERING LAB","DIGITAL ELECTRONICS LAB","INDUSTRIAL TRAINING","DISCIPLINE & EXTRA CURRICULAR"],
    4: ["Discrete Mathematics Structure","Managerial Economics and Financial Accounting","Technical Communication","Microprocessor & Interfaces","Database Management System","Theory Of Computation","Data Communication and Computer Networks","Microprocessor & Interfaces Lab","Database Management System Lab","Network Programming Lab","Linux Shell Programming Lab","Java Lab"],
    5: ["Information Theory & Coding", "Compiler Design", "Operating System", "Computer Graphics & Multimedia", "Analysis Of Algorithms", "Wireless Communication","Human Computer Interaction", "Computer Graphics & Multimedia Lab", "Compiler Design Lab", "Advance Java Lab"],
    6: ["Digital Image Processing","Machine Learning","Information Security System","Computer Architecture and Organization","Artificial Intelligence","Cloud Computing","Distributed System","Software Defined Network","Ecommerce & ERP","Digital Image Processing Lab","Machine Learning Lab","Python Lab","Mobile Application Development Lab"],
    7: ["Internet of Things","Internet of Things Lab","Cyber Security Lab","Big Data Analytics","Big Data Analytics Lab","Software Testing and Validation Lab"],
    8: ["Project Work", "Industrial Training", "Seminar"]
}

@admin_bp.route('/init_subjects')
def init_subjects():
    for sem, subjects in subjects_by_semester.items():
        for sub in subjects:
            # Avoid duplicate
            existing = Subject.query.filter_by(name=sub, semester=sem).first()
            if not existing:
                new_sub = Subject(name=sub, semester=sem, branch="CSE")  # branch fix CSE
                db.session.add(new_sub)
    db.session.commit()
    return "All subjects added successfully!"

students_data = [
    ("Ajay Lodha", "23CSE01"),
    ("Ankit Nayak", "23CSE02"),
    ("Ankit Singh Chouhan", "23CSE03"),
    ("Bhumika Lohar", "23CSE04"),
    ("Dhairya Sharma", "23CSE05"),
    ("Dharmendra Saini", "23CSE06"),
    ("Divyani Rajput", "23CSE07"),
    ("Granth Nema", "23CSE08"),
    ("Himani Mehra", "23CSE09"),
    ("Koushiki Pandya", "23CSE10"),
    ("Manish Lodha", "23CSE11"),
    ("Meet Rana", "23CSE12"),
    ("Mohammad Hussain Sindhi", "23CSE13"),
    ("Naksh Purohit", "23CSE14"),
    ("Pankaj Jangid", "23CSE15"),
    ("Payansh Jain", "23CSE16"),
    ("Purvansh Panchal", "23CSE17"),
    ("Rajat Pandya", "23CSE18"),
    ("Rohit", "23CSE19"),
    ("Rohit Bairagi", "23CSE20"),
    ("Somya Menariya", "23CSE21"),
    ("Sourabh Singh", "23CSE22")
]

@admin_bp.route('/init_students')
def init_students():
    for name, roll in students_data:
        existing = Student.query.filter_by(roll_number=roll).first()
        if not existing:
            new_student = Student(name=name, roll_number=roll, branch="CSE", semester=5)
            db.session.add(new_student)
    db.session.commit()
    return "All students added successfully!"