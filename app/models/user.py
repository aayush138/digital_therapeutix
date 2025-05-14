from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    license_number = db.Column(db.String(50), nullable=False)
    license_country = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(120), nullable=True)

    is_email_verified = db.Column(db.Boolean, default=False)
    is_license_verified = db.Column(db.Boolean, default=False)  # Manual approval for now

    registered_at = db.Column(db.DateTime, default=datetime.now)
    last_verification_reminder = db.Column(db.DateTime, nullable=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
