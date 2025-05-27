from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models.user import User, db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def restrict_to_admin():
    if not session.get('is_admin'):
        flash("Admin access only.", "danger")
        return redirect(url_for('auth.login'))

@admin_bp.route('/dashboard')
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)
    users = User.query.filter_by(is_email_verified=True, is_license_verified=False).order_by(User.registered_at.desc()).paginate(page=page, per_page=per_page)
    start = (users.page - 1) * users.per_page + 1 if users.total > 0 else 0
    end = min(users.page * users.per_page, users.total)
    return render_template("admin/dashboard.html", users=users, start=start, end=end)

@admin_bp.route('/approve/<int:user_id>')
def approve_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_license_verified = True
        db.session.commit()
        flash("User approved", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject/<int:user_id>')
def reject_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User rejected and removed", "info")
    return redirect(url_for('admin.dashboard'))
