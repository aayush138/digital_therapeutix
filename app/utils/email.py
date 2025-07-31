from flask_mail import Message
from flask import url_for, current_app
from app.extensions import mail
from app.utils.helpers import render_email_template



# Send email to user for verification & Account Completion
def send_verification_email(user_email, token):
    verify_url = url_for('auth.complete_application', token=token, _external=True)
    subject = "Continue Your Application - Digital Therapeutix"
    inner_html = f"""
        <h2>Complete Your Application</h2>
        <p>Hello,</p>
        <p>Thank you for choosing <strong>Digital Therapeutix</strong>. To continue your application, please click the button below:</p>
        <p><a href="{verify_url}" style="background: #14803c; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Complete Application</a></p>
        <p>This link is valid for 7 days.</p>
        <p>If you did not request this, please ignore this email.</p>
    """
    html_body = render_email_template(inner_html)
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)




# Send password reset email
def send_password_reset_email(user_email, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    subject = "Password Reset - Digital Therapeutix"
    inner_html = f"""
        <h2>Password Reset Request</h2>
        <p>Hello,</p>
        <p>We received a request to reset your password. Click the button below to proceed:</p>
        <p><a href="{reset_url}" style="background: #14803c; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Reset Password</a></p>
        <p>This link will expire in 24 hours. If you didn’t request this, no action is needed.</p>
    """
    html_body = render_email_template(inner_html)
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)    




# Notify admin of new user signup
def send_welcome_email_to_admin(admin_email, user_email):
    subject = "New User Signup - Digital Therapeutix"
    inner_html = f"""
        <h2>New User Registration</h2>
        <p>Dear Admin,</p>
        <p>A new user has signed up using the email address: <strong>{user_email}</strong>.</p>
        <p>Please log in to your dashboard to review their application.</p>
    """
    html_body = render_email_template(inner_html)
    msg = Message(subject=subject, recipients=[admin_email], html=html_body)
    mail.send(msg)




# Notify user of successful signup
def send_signup_notification_email(user_email):
    subject = "Signup Successful - Digital Therapeutix"
    inner_html = """
        <h2>Thank You for Signing Up!</h2>
        <p>Hello,</p>
        <p>Your application has been received and is currently under review.</p>
        <p>You will be notified via email once it has been approved, typically within 24–48 hours.</p>
    """
    html_body = render_email_template(inner_html)
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)




# Notify user of application approval
def send_application_approval_email(user_email):
    subject = "Application Approved - Digital Therapeutix"
    inner_html = """
        <h2>Application Approved</h2>
        <p>Hello,</p>
        <p>We’re pleased to inform you that your application has been <strong>approved</strong>.</p>
        <p>You can now log in to your account using your registered credentials.</p>
        <p>Welcome aboard!</p>
    """
    html_body = render_email_template(inner_html)
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)




#  Notify user of application rejection
def send_application_rejection_email(user_email):
    subject = "Application Rejected - Digital Therapeutix"
    inner_html = """
        <h2>Application Status Update</h2>
        <p>Hello,</p>
        <p>Thank you for your interest in Digital Therapeutix.</p>
        <p>After reviewing your application, we regret to inform you that it has been <strong>rejected</strong>.</p>
        <p>If you have questions, please feel free to contact our support team.</p>
    """
    html_body = render_email_template(inner_html)
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)  




# Notify user of account being blocked
def send_account_blocked_email(user_email):
    subject = "Account Blocked - Digital Therapeutix"
    inner_html = """
        <h2>Account Temporarily Blocked</h2>
        <p>Hello,</p>
        <p>Your account has been <strong>temporarily blocked</strong> due to suspicious activity.</p>
        <p>Please contact our support team for further assistance.</p>
    """
    html_body = render_email_template(inner_html)
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)




# Notify user of account being unblocked
def send_account_unblocked_email(user_email):
    subject = "Account Unblocked - Digital Therapeutix"
    inner_html = """
        <h2>Account Unblocked</h2>
        <p>Hello,</p>
        <p>Your account has been <strong>successfully unblocked</strong>.</p>
        <p>You may now log in and continue using the Digital Therapeutix platform.</p>
    """
    html_body = render_email_template(inner_html)
    msg = Message(subject=subject, recipients=[user_email], html=html_body)
    mail.send(msg)



