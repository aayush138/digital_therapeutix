import jwt, os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from flask import current_app, render_template_string, url_for

load_dotenv()

SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@example.com")
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://example.com")


# This function generates a JWT token for email verification 7-days Validity
def generate_verification_token(email, expires_days=7):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(days=expires_days)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')




# This function verifies the JWT token for email verification
def verify_verification_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['email']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None




# This function generates a JWT token for password reset
def generate_reset_token(email):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')




# This function verifies the JWT token for password reset
def verify_reset_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['email']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    



# This function generates a JWT token for user authentication
def generate_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_access_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    

# This function renders the email template with the provided inner HTML content
def render_email_template(inner_html: str) -> str:
    """
    Wraps the provided inner_html in a base email layout template.
    """
    base_template = """
    <!DOCTYPE html>
    <html>
      <body style="font-family: Inter, sans-serif; background-color: #f8f9fa; padding: 30px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 25px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
          <div style="text-align: center; margin-bottom: 30px;">
            <img src="{{ logo_url }}" alt="DTPx Logo" style="height: 48px; margin: auto;">
          </div>

          {{ body_content|safe }}

          <br><hr style="border: none; border-top: 1px solid #ddd;"><br>
          <p style="font-size: 14px; color: #555;">
            Regards,<br>
            <strong>Digital Therapeutix Team</strong><br>
            <a href="mailto:{{ support_email }}" style="color: #14803c; text-decoration:none;">{{ support_email }}</a><br>
            <a href="{{ website_url }}" style="color: #14803c; text-decoration:none;">{{ website_url|replace("https://", "") }}</a>
          </p>
        </div>
      </body>
    </html>
    """

    return render_template_string(
        base_template,
        body_content=inner_html,
        support_email=SUPPORT_EMAIL,
        website_url=WEBSITE_URL,
        logo_url=f"{WEBSITE_URL}/static/images/favicon.png"  # replace with your actual domain
    )