import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=10)

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    ADMINS = [
        {
            "name": os.environ.get("ADMIN_1_NAME"),
            "email": os.environ.get("ADMIN_1_EMAIL"),
            "password": os.environ.get("ADMIN_1_PASSWORD"),
        },
        {
            "name": os.environ.get("ADMIN_2_NAME"),
            "email": os.environ.get("ADMIN_2_EMAIL"),
            "password": os.environ.get("ADMIN_2_PASSWORD"),
        },
        {
            "name": os.environ.get("ADMIN_3_NAME"),
            "email": os.environ.get("ADMIN_3_EMAIL"),
            "password": os.environ.get("ADMIN_3_PASSWORD"),
        },
        {
            "name": os.environ.get("ADMIN_4_NAME"),
            "email": os.environ.get("ADMIN_4_EMAIL"),
            "password": os.environ.get("ADMIN_4_PASSWORD"),
        },
        {
            "name": os.environ.get("ADMIN_5_NAME"),
            "email": os.environ.get("ADMIN_5_EMAIL"),
            "password": os.environ.get("ADMIN_5_PASSWORD"),
        },
    ]