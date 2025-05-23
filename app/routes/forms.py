from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


# Signup form for new users
class SignupForm(FlaskForm):
    full_name = StringField("Full Legal Name *", validators=[DataRequired()])
    email = StringField("Work Email *", validators=[DataRequired(), Email()])
    
    password = PasswordField("Password *", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password *", validators=[
        DataRequired(), EqualTo("password", message="Passwords must match")
    ])
    
    submit = SubmitField("Sign Up")


class CompleteApplicationForm(FlaskForm):
    # Basic Info
    preferred_name = StringField("Preferred Name *", validators=[DataRequired()])
    backup_email = StringField("Backup Email Address", validators=[Optional(), Email()])
    phone_number = StringField("Phone Number *", validators=[DataRequired()])

    # Address
    clinic_name = StringField("Clinic/Hospital Name *", validators=[DataRequired()])
    clinic_email = StringField("Clinic/Hospital Email Address *", validators=[DataRequired(), Email()])
    address_street = StringField("Street Address *", validators=[DataRequired()])
    address_city = StringField("City *", validators=[DataRequired()])
    address_state = StringField("State/Province *", validators=[DataRequired()])
    address_zip = StringField("ZIP/Postal Code *", validators=[DataRequired()])
    address_country = StringField("Country *", validators=[DataRequired()])

    # License
    license_number = StringField("Medical License Number *", validators=[DataRequired()])
    license_country = StringField("Issuing State/Country *", validators=[DataRequired()])

    # Credentials
    medical_degree = StringField("Medical Degree *", validators=[DataRequired()])
    specialty = StringField("Medical Specialty *", validators=[DataRequired()])
    subspecialty = StringField("Subspecialty (If Applicable)", validators=[Optional()])
    current_employer = StringField("Current Employer *", validators=[DataRequired()])

    submit = SubmitField("Submit Application")    



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