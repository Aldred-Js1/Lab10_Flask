from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField 
from wtforms.validators import InputRequired, Email, Length 

class RegisterForm(FlaskForm):
    # Combined into one clean definition
    email = StringField('Email', 
                        validators=[InputRequired(), Email(), Length(max=50)],
                        description="Your school email address")
    
    password = PasswordField('Password', 
                             validators=[InputRequired(), Length(min=4, max=80)])
    
    submit = SubmitField('Register')
    
class LoginForm(FlaskForm): 
    email = StringField('Email', validators=[InputRequired(), Email()]) 
    password = PasswordField('Password', validators=[InputRequired()]) 
    submit = SubmitField('Login')
