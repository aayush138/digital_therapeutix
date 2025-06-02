from flask import Blueprint, render_template, session, redirect, url_for, flash, g, request, jsonify
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
        g.doctor_user = session.get('doctor_name', 'Doctor')
        g.license_number = session.get('license_number', '#000000')

@dashboard_bp.route('/')
def home():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    return render_template('dashboard/home.html', active_page='home', doctor_name=g.doctor_user, license_number=g.license_number)

@dashboard_bp.route('/cases')
def cases():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    # You can fetch and pass cases here if needed
    return render_template('dashboard/cases.html', active_page='cases', doctor_name=g.doctor_user, license_number=g.license_number)

@dashboard_bp.route('/help')
def help():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    return render_template('dashboard/help.html', active_page='help', doctor_name=g.doctor_user, license_number=g.license_number)



@dashboard_bp.route('/analyze', methods=['POST'])
def analyze():
    fasta_file = request.files.get('fasta')
    notes = request.form.get('notes')
    model = request.form.get('model')
    if not fasta_file:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
    fasta_content = fasta_file.read().decode('utf-8', errors='ignore')
    # TODO: Process fasta_content, notes, model as needed...
    return jsonify({'status': 'success'})