from flask import render_template, flash, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from app.auth.models import User
from app.auth.forms import LoginForm
from app.auth import auth_bp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        current_app.logger.debug(f"User '{current_user.username}' is already authenticated, redirecting")
        return redirect(url_for("weather_bp.index"))
    else:
        login_form = LoginForm()
        if login_form.validate_on_submit():
            username = login_form.username.data
            password = login_form.password.data
            user = User.query.filter_by(username=username).first()
            if user is not None and check_password_hash(user.password, password):
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
    current_app.logger.info(f"User '{current_user.username}' logging out")
    logout_user()
    flash("Logged Out", category="success")
    return redirect(url_for("auth_bp.login"))
