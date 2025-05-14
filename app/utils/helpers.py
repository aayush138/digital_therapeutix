import jwt
from datetime import datetime, timedelta
from flask import current_app, session




# This function generates a JWT token for email verification
def generate_verification_token(email):
    payload = {
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=24)
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
        'exp': datetime.utcnow() + timedelta(hours=24)
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
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_access_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None