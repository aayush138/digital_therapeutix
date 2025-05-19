from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.forms import SignupForm, ForgotPasswordForm, ResetPasswordForm, LoginForm
from app.models.user import User, db
from app.utils.helpers import generate_verification_token, generate_reset_token, verify_reset_token, generate_access_token
from app.utils.email import send_verification_email, send_password_reset_email

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
            flash("Email already registered", "danger")
            return render_template('auth/signup.html', form=form)

        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            license_number=form.license_number.data,
            license_country=form.license_country.data,
            institution=form.institution.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        token = generate_verification_token(new_user.email)
        send_verification_email(new_user.email, token)

        flash("Signup successful. Please check your email to verify your account.", "success")
        return redirect(url_for('auth.login'))
    return render_template('auth/signup.html', form=form)




# For the login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        remember_me = form.remember.data

        if not user:
            flash("No account found with this email.", "danger")
            return render_template("auth/login.html", form=form)
        
        if not user.check_password(form.password.data):
            flash("Incorrect password", "danger")
            return render_template("auth/login.html", form=form)

        if not user.is_email_verified:
            flash("Email not verified. Please check your inbox.", "warning")
            return render_template("auth/login.html", form=form)
        
        if not user.is_license_verified:
            flash("Your license is under review. Please wait for admin approval.", "warning")
            return render_template("auth/login.html", form=form)
        
         # Set session permanence based on remember_me
        session.permanent = remember_me

        # All good – set JWT + session
        token = generate_access_token(user.id)
        session['jwt_token'] = token
        session['user_id'] = user.id
        session['user_email'] = user.email
        flash("Logged in successfully!", "success")
        return redirect(url_for("dashboard.index"))  # or your actual dashboard

    return render_template("auth/login.html", form=form)




# For the logout route
@auth_bp.route('/logout', methods=['POST'])
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
            send_password_reset_email(user.email, token)
        flash("If the email is registered, a reset link has been sent.", "info")
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash("Invalid or expired token", "danger")
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found", "danger")
        return redirect(url_for('auth.signup'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password reset successful. Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)
