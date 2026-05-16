# Step 1: Import necessary libraries and modules 
from flask import Flask, render_template, redirect, url_for, request, flash 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, login_user, login_required, logout_user, current_user 
from werkzeug.security import generate_password_hash, check_password_hash 
import os 

# Step 2: Import forms and models 
from forms import RegisterForm, LoginForm 
from models import db, User, Student 

# Step 3: Initialize Flask app
app = Flask(__name__, instance_relative_config=True) 

# Step 4: Configuration settings
app.config['SECRET_KEY'] = 'my-secret-key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# Near your other app.config settings
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create the folder automatically if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Step 5: Initialize database and login manager 
db.init_app(app) 
login_manager = LoginManager(app) 
login_manager.login_view = 'login'

# Step 6: User loader function
@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id)) 

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('home.html', name="Mark Aldred A. Reyes", section="BSECE 1B")

@app.route('/about') 
def about(): 
    return render_template('about.html') 

@app.route('/contact') 
def contact(): 
    return render_template('contact.html') 

@app.route('/register', methods=['GET', 'POST']) 
def register(): 
    form = RegisterForm() 
    if form.validate_on_submit(): 
        print("Form submitted successfully!") 
        
        # CHECK: Prevent duplicate user emails
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please login.")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(form.password.data) 
        user = User(email=form.email.data, password=hashed_pw)  
        db.session.add(user) 
        db.session.commit() 
        flash("Registration successful!") 
        return redirect(url_for('login')) 
    
    elif request.method == 'POST':
        print("Validation failed.")
        print(f"Errors: {form.errors}")
        
    return render_template('register.html', form=form) 

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

@app.route('/logout')
@login_required 
def logout(): 
    logout_user() 
    flash("You have been logged out.") 
    return redirect(url_for('home')) 

@app.route('/students')
@login_required
def students():
    students_list = Student.query.order_by(Student.full_name).all()
    return render_template('students.html', students=students_list) 

@app.route('/add_student', methods=['POST']) 
@login_required 
def add_student(): 
    name = request.form.get('name') 
    email = request.form.get('email') 

    existing_student = Student.query.filter_by(email=email).first()
    if existing_student:
        flash("Error: A student with this email is already in the list!")
        return redirect(url_for('students'))

    new_student = Student(full_name=name, email=email) 
    db.session.add(new_student) 
    db.session.commit() 
    flash("Student added successfully!")
    return redirect(url_for('students')) 

@app.route('/delete-student/<int:id>') 
@login_required 
def delete_student(id): 
    # Add this Role Check
    if current_user.role != 'admin':
        flash("Access Denied: Only Admins can delete records.")
        return redirect(url_for('students'))

    student = Student.query.get_or_404(id) 
    db.session.delete(student) 
    db.session.commit() 
    flash("Student record deleted.")
    return redirect(url_for('students')) 

@app.errorhandler(404) 
def page_not_found(e): 
    return render_template('404.html'), 404


from werkzeug.utils import secure_filename # Add this import at the top of app.py

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Check if a file was uploaded
        file = request.files.get('profile_pic')
        if file and file.filename != '':
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Update the database for the logged-in user
            current_user.profile_pic = filename
            db.session.commit()
            flash("Profile updated successfully!")
            
    return render_template('profile.html')

# Step 9: Run application
if __name__ == '__main__': 
    if not os.path.exists(os.path.join(app.instance_path, 'app.db')): 
        os.makedirs(app.instance_path, exist_ok=True) 
        with app.app_context(): 
            db.create_all() 
    app.run(debug=True)