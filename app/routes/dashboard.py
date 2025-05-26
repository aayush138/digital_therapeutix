from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def index():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    return render_template('dashboard/index.html')