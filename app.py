from flask import Flask,render_template,Blueprint,redirect,request,url_for,session,flash
from werkzeug.security import generate_password_hash
from routes.admin import createadmin
from db import db
from dotenv import load_dotenv
import os





from routes.auth import auth_bp 
from routes.admin import admin_bp
from routes.faculty import faculty_bp

app=Flask(__name__)


# db_path = ensure_db()
# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','sqlite:///sms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY']=os.getenv('SECRET_KEY','somyasecretkey')

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(faculty_bp)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    with app.app_context():
        from models.models import *
        db.create_all()
        createadmin()

        app.run(debug=True)
        
