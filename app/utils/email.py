from flask_mail import Message
from flask import url_for, current_app
from app.extensions import mail


# This function sends a verification email to the user
def send_verification_email(user_email, token):
    verify_url = url_for('auth.complete_application', token=token, _external=True)
    subject = "Continue Your Application - Digital Therapeutix"
    html_body = f"""
    <h3>Welcome to Digital Therapeutix</h3>
    <p>Click below to complete your application. This link will expire in 7 days:</p>
    <a href="{verify_url}">{verify_url}</a>
    """
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)




# This function sends a password reset email to the user
def send_password_reset_email(user_email, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    subject = "Password Reset - Digital Therapeutix"
    html_body = f"""
    <h3>Password Reset Request</h3>
    <p>Click below to reset your password. This link will expire in 24 hours.</p>
    <a href="{reset_url}">Reset Password</a>
    """

    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)




# Send a welcome email to the admin when a new user signs up
def send_welcome_email_to_admin(admin_email, user_email):
    subject = "New User Signup - Digital Therapeutix"
    html_body = f"""
    <h3>New User Signup</h3>
    <p>A new user has signed up with the email: {user_email}</p>
    <p>Please review their application.</p>
    """
    
    msg = Message(subject=subject, recipients=[admin_email], html=html_body)
    mail.send(msg)


# Send a notification email to the user about successful signup
def send_signup_notification_email(user_email):
    subject = "Signup Successful - Digital Therapeutix"
    html_body = """
    <h3>Thank you for signing up!</h3>
    <p>Your application has been received and is under review. You will receive an email notification once it has been approved. Usually it takes 24- 48 Hours</p>
    """
    
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)


# Send a notification email to the user about application approval
def send_application_approval_email(user_email):
    subject = "Application Approved - Digital Therapeutix"
    html_body = """
    <h3>Congratulations!</h3>
    <p>Your application has been approved. You can now log in to your account.</p>
    """
    
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)

# Send a notification email to the user about application rejection
def send_application_rejection_email(user_email):
    subject = "Application Rejected - Digital Therapeutix"
    html_body = """
    <h3>Application Update</h3>
    <p>We regret to inform you that your application has been rejected. If you have any questions, please contact support.</p>
    """
    
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)            