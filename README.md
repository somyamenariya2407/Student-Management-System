# Student Management System (SMS)

A web-based **Student Management System** built with **Flask**, **SQLite**, **SQLAlchemy**, and **Bootstrap**. The application provides separate Admin and Faculty panels for managing students, faculty members, subjects, attendance, marks, and semester-wise marksheets.

## Features

### Admin

- Secure admin login
- Admin dashboard with total students, faculties, and subjects
- Add, view, edit, and delete faculty records
- Assign subjects/courses to faculty members
- Add, view, edit, and delete student records
- Manage semester-wise subjects
- Seed default CSE subjects and sample students

### Faculty

- Faculty login and dashboard
- View assigned course details and syllabus
- Mark student attendance for assigned subjects
- View attendance records by course, date, and status
- Generate attendance summaries with percentage
- Add and update student marks
- Filter marks by grade and marks range
- Generate student marksheets with SGPA calculation
- View faculty profile

## Tech Stack

- **Backend:** Flask
- **Database:** SQLite
- **ORM:** Flask-SQLAlchemy / SQLAlchemy
- **Frontend:** HTML, CSS, Bootstrap 5, Bootstrap Icons
- **Template Engine:** Jinja2
- **Authentication:** Flask sessions with Werkzeug password hashing
- **Environment Variables:** python-dotenv

## Project Structure

```text
Student-Management-System/
|-- app.py
|-- db.py
|-- requirement.txt
|-- README.md
|-- ER-Diagram.png
|-- models/
|   `-- models.py
|-- routes/
|   |-- admin.py
|   |-- auth.py
|   `-- faculty.py
|-- static/
|   |-- css/
|   |   `-- home.css
|   `-- images/
|       |-- avtar.png
|       |-- home.jpg
|       |-- syllabus.png
|       `-- Syllabus.pdf
`-- templates/
    |-- home.html
    |-- login.html
    |-- admin/
    `-- faculty/
```

## Database Design

Main database entities:

- `User` - stores admin and faculty accounts
- `Student` - stores student details
- `Subject` - stores semester-wise subjects
- `FacultySubject` - maps faculty members with subjects
- `Attendance` - stores daily attendance records
- `Marks` - stores subject-wise student marks and grades

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.10 or above
- pip
- Git

### Installation

1. Install the Zip file

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirement.txt
```

4. Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///sms.db
```

If `DATABASE_URL` is not provided, the app uses `sqlite:///sms.db` by default.

5. Run the application:

```bash
python app.py
```

6. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Default Admin Login

When the app starts for the first time, it automatically creates a default admin account:

> Important: Change the default admin credentials before using this project in production.

## Main Routes

### Public/Auth Routes

| Route | Description |
| --- | --- |
| `/` | Home page |
| `/login` | Login page |
| `/logout` | Logout current user |

### Admin Routes

| Route | Description |
| --- | --- |
| `/admin/dashboard` | Admin dashboard |
| `/admin/manage_faculty` | Faculty management page |
| `/admin/add_faculty` | Add faculty |
| `/admin/view_faculty` | View faculty list |
| `/admin/manage_student` | Student management page |
| `/admin/add_student` | Add student |
| `/admin/view_student` | View students |
| `/admin/manage_subject` | Manage subjects |

### Faculty Routes

| Route | Description |
| --- | --- |
| `/faculty/dashboard` | Faculty dashboard |
| `/faculty/view_details` | View assigned details and syllabus |
| `/faculty/attendance` | Mark attendance |
| `/faculty/view_attendance` | View attendance records |
| `/faculty/attendance_summary` | Attendance summary |
| `/faculty/marks` | Add/update marks |
| `/faculty/view_marks` | View and filter marks |
| `/faculty/marksheet_select` | Select student for marksheet |
| `/faculty/marksheet` | Generate marksheet |
| `/faculty/profile` | View profile |


## Notes

- The SQLite database is created automatically when `python app.py` is executed.
- Faculty users are created by the admin.
- Faculty members can access only their assigned courses.
- Attendance can be marked only for the current date.
- The project uses Bootstrap CDN links, so an internet connection is recommended for full styling.

## Future Improvements

- Add student login panel
- Add role-based decorators for cleaner route protection
- Add password reset/change password functionality
- Add pagination and search for large datasets
- Export attendance, marks, and marksheets as PDF/Excel
- Add automated tests

## Author

Developed by **Somya Menariya**.
