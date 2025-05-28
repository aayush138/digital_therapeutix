from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Step 1: Minimal fields
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    is_email_verified = db.Column(db.Boolean, default=False)
    is_license_verified = db.Column(db.Boolean, default=False)  # admin approves
    is_blocked = db.Column(db.Boolean, default=False)

    # Step 2: Application details
    preferred_name = db.Column(db.String(120), nullable=True)
    backup_email = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(30), nullable=True)

    clinic_name = db.Column(db.String(120), nullable=True)
    clinic_email = db.Column(db.String(120), nullable=True)
    address_street = db.Column(db.String(200), nullable=True)
    address_city = db.Column(db.String(100), nullable=True)
    address_state = db.Column(db.String(100), nullable=True)
    address_zip = db.Column(db.String(20), nullable=True)
    address_country = db.Column(db.String(100), nullable=True)

    license_number = db.Column(db.String(50), nullable=True)
    license_country = db.Column(db.String(100), nullable=True)

    medical_degree = db.Column(db.String(100), nullable=True)
    specialty = db.Column(db.String(100), nullable=True)
    subspecialty = db.Column(db.String(100), nullable=True)
    current_employer = db.Column(db.String(120), nullable=True)

    # Meta
    registered_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_verification_reminder = db.Column(db.DateTime, nullable=True)
    verification_token = db.Column(db.String(256), nullable=True)
    verification_token_expiry = db.Column(db.DateTime(timezone=True), nullable=True)
    reset_token = db.Column(db.String(256), nullable=True)
    reset_token_expiry = db.Column(db.DateTime(timezone=True), nullable=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
