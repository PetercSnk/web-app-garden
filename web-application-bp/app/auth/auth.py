from flask import render_template, request, flash, redirect, url_for, current_app
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app.auth.models import User
from app.auth import auth_bp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user is not None and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash("Logged In", category="success")
            current_app.logger.info(f"user '{username}' successfully logged in")
            return redirect(url_for("weather_bp.index"))
        else:
            flash("Error", category="error")
            current_app.logger.error(f"user '{username}' failed to log in")
    return render_template("auth/login.html", user=current_user)


@auth_bp.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash("Logged Out", category="success")
    current_app.logger.info(f"user '{username}' successfully logged out")
    return redirect(url_for("auth_bp.login"))
