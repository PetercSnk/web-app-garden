from flask import render_template, flash, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from app.auth.models import User
from app.auth.forms import LoginForm, AdminForm
from app.auth import auth_bp
from app import db


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticates users if username and password exist in user table."""
    if current_user.is_authenticated:
        current_app.logger.debug(f"User '{current_user.username}' is already authenticated, redirecting")
        return redirect(url_for("weather_bp.index"))
    else:
        login_form = LoginForm()
        if login_form.validate_on_submit():
            username = login_form.username.data
            password = login_form.password.data
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Logged In", category="success")
                current_app.logger.info(f"User '{username}' successfully logged in")
                return redirect(url_for("weather_bp.index"))
            else:
                flash("Error", category="error")
                current_app.logger.error(f"User '{username}' failed to log in")
        return render_template("auth/login.html", user=current_user, login_form=login_form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Deauthenticates users."""
    current_app.logger.info(f"User '{current_user.username}' logging out")
    logout_user()
    flash("Logged Out", category="success")
    return redirect(url_for("auth_bp.login"))


@auth_bp.route("/admin")
@login_required
def admin():
    admin_form = AdminForm()
    if admin_form.validate_on_submit():
        user = User.query.filter_by(username=current_user).first()
        user.username = admin_form.username.data
        user.password = admin_form.password.data
        db.session.commit()
        current_app.logger.info("User account updated")
    pass
