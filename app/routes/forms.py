from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


# Signup form for new users
class SignupForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    license_number = StringField("License Number", validators=[DataRequired()])
    license_country = StringField("Issuing Country", validators=[DataRequired()])
    institution = StringField("Institution (Optional)")
    
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match")
    ])
    
    submit = SubmitField("Sign Up")



#  Login form for new users
class LoginForm(FlaskForm):
    email = StringField("Email Address *", validators=[DataRequired(), Email()])
    password = PasswordField("Password *", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")    




# Forgot password form for users who want to reset their password
class ForgotPasswordForm(FlaskForm):
    email = StringField("Registered Email *", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")




# Reset password form to set a new password
class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password *", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password *", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match")
    ])
    submit = SubmitField("Reset Password")