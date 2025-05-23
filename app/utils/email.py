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