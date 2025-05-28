from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from app.routes.forms import SignupForm, ForgotPasswordForm, ResetPasswordForm, LoginForm, CompleteApplicationForm
from app.models.user import User, db
from app.utils.helpers import generate_verification_token, generate_reset_token, verify_reset_token, generate_access_token, verify_verification_token
from app.utils.email import send_verification_email, send_password_reset_email, send_signup_notification_email, send_welcome_email_to_admin

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')



@auth_bp.route('/')
def root():
    return redirect(url_for('auth.login'))


# For the signup route
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash("Email already registered.", "danger")
            return redirect(url_for('auth.login'))

        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data
        )
        new_user.set_password(form.password.data)

        # Send a verification email with a 7-day token
        token = generate_verification_token(new_user.email, expires_days=7)
        new_user.verification_token = token
        new_user.verification_token_expiry = datetime.now(timezone.utc) + timedelta(days=7)
        db.session.add(new_user)
        db.session.commit()
        send_verification_email(new_user.email, token)

        flash("Signup successful. Please check your email to complete the application. Link valid for 7 days.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html', form=form)

# For the completing signup application.
@auth_bp.route('/complete-application/<token>', methods=['GET', 'POST'])
def complete_application(token):
    email = verify_verification_token(token)
    if not email:
        flash("The application link has expired or is invalid.", "danger")
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.signup'))
    
    if not user.verification_token or user.verification_token != token or not user.verification_token_expiry or (
        (user.verification_token_expiry.tzinfo is None and user.verification_token_expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc))
        or
        (user.verification_token_expiry.tzinfo is not None and user.verification_token_expiry < datetime.now(timezone.utc))
    ):
        flash("Your application has already been submitted. You will receive an email notification once it has been reviewed by our team.", "danger")
        return redirect(url_for('auth.signup'))


    form = CompleteApplicationForm(obj=user)

    if form.validate_on_submit():
        form.populate_obj(user)
        user.is_email_verified = True
        user.verification_token = None
        user.verification_token_expiry = None
        db.session.commit()
        send_signup_notification_email(user.email)
        for admin in current_app.config["ADMINS"]:
            send_welcome_email_to_admin(admin["email"], user.email)
        flash("Application completed. Awaiting admin approval.", "success")
        return render_template("auth/complete_application.html", form=form, show_modal=True, user_email=user.email)

    return render_template("auth/complete_application.html", form=form)




# For the login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))
    elif session.get('user_id'):
        return redirect(url_for('dashboard.index'))
    

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember_me = form.remember.data

        # Check if admin
        admin = next((a for a in current_app.config["ADMINS"] 
                      if a["email"] == email and a["password"] == password), None)
        if admin:
            session.permanent = remember_me
            session['is_admin'] = True
            session['admin_name'] = admin["name"]
            session['admin_email'] = admin["email"]
            flash("Logged in as admin", "success")
            return redirect(url_for("admin.dashboard"))

        # Check if doctor
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with this email.", "danger")
            return render_template("auth/login.html", form=form)

        if not user.check_password(password):
            flash("Incorrect password", "danger")
            return render_template("auth/login.html", form=form)

        if not user.is_email_verified:
            flash("Email not verified. Please check your inbox.", "warning")
            return render_template("auth/login.html", form=form)

        if not user.is_license_verified:
            flash("Your license is under review. Please wait for admin approval.", "warning")
            return render_template("auth/login.html", form=form)
        
        if user.is_blocked:
            flash("Your account is blocked. Please contact support.", "danger")
            return render_template("auth/login.html", form=form)

        # Valid doctor login
        session.permanent = remember_me
        token = generate_access_token(user.id)
        session['jwt_token'] = token
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['is_admin'] = False

        flash("Logged in successfully!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html", form=form)



# For the logout route
@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))




# For the email verification route
@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    from app.utils.helpers import verify_verification_token
    email = verify_verification_token(token)
    if not email:
        flash("Invalid or expired verification link", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found", "danger")
        return redirect(url_for('auth.signup'))

    if user.is_email_verified:
        flash("Email is already verified", "info")
    else:
        user.is_email_verified = True
        db.session.commit()
        flash("Email successfully verified! You may now log in.", "success")

    return redirect(url_for('auth.login'))




# Forgot password and reset password routes
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_reset_token(user.email)
            user.reset_token = token
            user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry
            db.session.commit()
            send_password_reset_email(user.email, token)
        flash("If the email is registered, a reset link has been sent.", "info")
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    user = User.query.filter_by(email=email).first() if email else None
    
    if not user or user.reset_token != token or not user.reset_token_expiry or ((user.reset_token_expiry.tzinfo is None and user.reset_token_expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)) or (user.reset_token_expiry.tzinfo is not None and user.reset_token_expiry < datetime.now(timezone.utc))):
        if user:
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
        flash("This reset link is invalid or has already been used.", "danger")
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None  # Invalidate the token after use
        user.reset_token_expiry = None
        db.session.commit()
        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)