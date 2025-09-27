from flask import Blueprint,render_template,redirect,request,url_for,session,flash
from models.models import User,db
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':

        email= request.form['email'].strip()
        password= request.form['password'].strip()

        if not email or not password:
            flash("Email and Password required.","danger")
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            session['user_id']=user.id
            session['user_name']=user.name
            session['role']=user.role
            session['email']=user.email

          

            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('faculty.faculty_dashboard')) 
        else:
            flash('Invalid Credentials!! Try again ', 'danger')
            return redirect(url_for('auth.login'))
        
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.",'success')
    return redirect(url_for('home'))

