from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models.user import User

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.before_request
def restrict_blocked_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user and user.is_blocked:
            session.clear()
            flash("Your account is blocked. Please contact support.", "danger")
            return redirect(url_for('auth.login'))

@dashboard_bp.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    return render_template('dashboard/index.html')