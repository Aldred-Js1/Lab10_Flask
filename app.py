# Step 1: Import necessary libraries and modules 
from flask import Flask, render_template, redirect, url_for, request, flash 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, login_user, login_required, logout_user, current_user 
from werkzeug.security import generate_password_hash, check_password_hash 

# Step 2: Import forms and models 
from forms import RegisterForm, LoginForm 
from models import db, User, Student 

import os 

# Step 3: Initialize Flask app with instance-relative config 
app = Flask(__name__, instance_relative_config=True) 

# Step 4: Debug logs for development (Optional) 
current_working_directory = os.getcwd() 
static_folder_path = app.static_folder 
print(f"DEBUG: Current working directory (os.getcwd()): {current_working_directory}") 
print(f"DEBUG: Flask static folder (app.static_folder): {static_folder_path}") 
print(f"DEBUG: Does static folder exist at app.static_folder? {os.path.isdir(static_folder_path)}") 

css_file_path = os.path.join(static_folder_path, 'css', 'style.css') 
image_file_path = os.path.join(static_folder_path, 'images', 'TUP.png') 
print(f"DEBUG: Expected style.css path: {css_file_path}") 
print(f"DEBUG: Does style.css exist at expected path? {os.path.exists(css_file_path)}") 
print(f"DEBUG: Expected TUP.png path: {image_file_path}") 
print(f"DEBUG: Does TUP.png exist at expected path? {os.path.exists(image_file_path)}") 

# Step 5: Configuration settings for secret key and database URI 
app.config['SECRET_KEY'] = 'my-secret-key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# Step 6: Initialize database and login manager 
db.init_app(app) 
login_manager = LoginManager(app) 
login_manager.login_view = 'login'  # redirect to login if unauthorized

# Step 7: User loader function required by Flask-Login 
@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id)) 

# Step 8: Define app routes 

# Home route 
@app.route('/') 
def home(): 
    return render_template('home.html') 

# About page 
@app.route('/about') 
def about(): 
    return render_template('about.html') 

# Contact page 
@app.route('/contact') 
def contact(): 
    return render_template('contact.html') 

# Register new user 
@app.route('/register', methods=['GET', 'POST']) 
def register(): 
    form = RegisterForm() 
    if form.validate_on_submit(): 
        hashed_pw = generate_password_hash(form.password.data) 
        user = User(email=form.email.data, password=hashed_pw) 
        db.session.add(user) 
        db.session.commit() 
        flash("Registration successful!") 
        return redirect(url_for('login')) 
    return render_template('register.html', form=form) 

# Login existing user 
@app.route('/login', methods=['GET', 'POST']) 
def login(): 
    form = LoginForm() 
    if form.validate_on_submit(): 
        user = User.query.filter_by(email=form.email.data).first() 
        if user and check_password_hash(user.password, form.password.data): 
            login_user(user) 
            flash("Logged in successfully.") 
            return redirect(url_for('students')) 
        else: 
            flash("Invalid email or password.") 
    return render_template('login.html', form=form) 

# Logout user 
@app.route('/logout')
@login_required 
def logout(): 
    logout_user() 
    flash("You have been logged out.") 
    return redirect(url_for('home')) 

# Display all students 
@app.route('/students') 
@login_required 
def students(): 
    student_list = Student.query.all() 
    return render_template('students.html', students=student_list) 

# Add new student 
@app.route('/add-student', methods=['POST']) 
@login_required 
def add_student(): 
    name = request.form['name'] 
    email = request.form['email'] 
    student = Student(full_name=name, email=email) 
    db.session.add(student) 
    db.session.commit() 
    return redirect(url_for('students')) 

# Delete a student 
@app.route('/delete-student/<int:id>') 
@login_required 
def delete_student(id): 
    student = Student.query.get_or_404(id) 
    db.session.delete(student) 
    db.session.commit() 
    return redirect(url_for('students')) 

# Step 9: Run the application and create the database if not yet created 
if __name__ == '__main__': 
    if not os.path.exists(os.path.join(app.instance_path, 'app.db')): 
        os.makedirs(app.instance_path, exist_ok=True) 
        with app.app_context(): 
            db.create_all() 
    app.run(debug=True)