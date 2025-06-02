from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify, g, current_app
from app.models.user import User, db
from app.utils.email import send_application_approval_email, send_application_rejection_email, send_account_unblocked_email, send_account_blocked_email

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def admin_before_request():
    if not session.get('is_admin'):
        flash("Admin access only.", "danger")
        return redirect(url_for('auth.login'))
    g.admin_user = session.get('admin_name', 'Admin')

@admin_bp.route('/dashboard')
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)
    users = User.query.filter_by(is_email_verified=True, is_license_verified=False).order_by(User.registered_at.desc()).paginate(page=page, per_page=per_page)
    start = (users.page - 1) * users.per_page + 1 if users.total > 0 else 0
    end = min(users.page * users.per_page, users.total)
    return render_template("admin/dashboard.html", users=users, admin_user=g.admin_user, start=start, end=end, active_page='verify', user_template="admin/verify.html")

@admin_bp.route('/users')
def all_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)
    users = User.query.filter_by(is_email_verified=True, is_license_verified=True)\
        .order_by(User.registered_at.desc())\
        .paginate(page=page, per_page=per_page)
    start = (users.page - 1) * users.per_page + 1 if users.total > 0 else 0
    end = min(users.page * users.per_page, users.total)
    return render_template("admin/dashboard.html", users=users, start=start, end=end, admin_user=g.admin_user, active_page='users', user_template="admin/user.html")


# User Licence Verification
@admin_bp.route('/approve/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_license_verified = True
        db.session.commit()
        send_application_approval_email(user.email)
        flash("User approved successfully!", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject/<int:user_id>', methods=['POST'])
def reject_user(user_id):
    user = User.query.get(user_id)
    if user:
        send_application_rejection_email(user.email)
        db.session.delete(user)
        db.session.commit()
        flash("User rejected successfully!", "danger")
    return redirect(url_for('admin.dashboard'))

# User Details
@admin_bp.route('/user/<int:user_id>/details')
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        # Basis Details
        "id": user.id,
        "is_blocked": user.is_blocked,
        "full_name": user.full_name,
        "preferred_name": user.preferred_name,
        "email": user.email,
        "backup_email": user.backup_email,
        "register_date": user.registered_at.strftime('%b %d %Y') if getattr(user, "registered_at", None) else "",
        "phone_number": user.phone_number,

        # Address Details
        "clinic_name": user.clinic_name,
        "clinic_email": user.clinic_email,
        "address_street": user.address_street,
        "address_city": user.address_city,
        "address_state": user.address_state,
        "address_zip": user.address_zip,
        "address_country": user.address_country,

        # License Details
        "license_number": user.license_number,
        "license_country": user.license_country,

        # Credentials
        "medical_degree": user.medical_degree,
        "specialty": user.specialty,
        "subspecialty": user.subspecialty,
        "current_employer": user.current_employer,
    })

@admin_bp.route('/search/users')
def search_users():
    q = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)
    verified = request.args.get('verified', 'false') == 'true'
    query = User.query.filter(
        User.is_email_verified == True,
        User.is_license_verified == verified,
        (User.full_name.ilike(f"%{q}%")) | (User.license_number.ilike(f"%{q}%"))
    ).order_by(User.registered_at.desc())
    users = query.paginate(page=page, per_page=per_page)
    # Choose the correct partial
    partial = "admin/user.html" if verified else "admin/verify.html"
    rows = render_template(partial, users=users)
    return jsonify({'rows': rows})



# Block/Unblock User
@admin_bp.route('/block/<int:user_id>', methods=['POST'])
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = True
    db.session.commit()
    send_account_blocked_email(user.email)
    flash("User blocked.", "danger")
    return redirect(url_for('admin.all_users'))

@admin_bp.route('/unblock/<int:user_id>', methods=['POST'])
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = False
    db.session.commit()
    send_account_unblocked_email(user.email)
    flash("User unblocked.", "success")
    return redirect(url_for('admin.all_users'))