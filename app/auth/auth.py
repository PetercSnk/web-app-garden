from flask import request, render_template, flash, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.auth.models import User
from app.auth.forms import LoginForm, AdminForm
from app.auth import auth_bp
from app import db


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticates users."""
    if current_user.is_authenticated:
        return redirect(url_for("weather_bp.index"))
    else:
        login_form = LoginForm()
        if request.method == "POST" and login_form.validate():
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
        return render_template("auth/login.html",
                               user=current_user,
                               login_form=login_form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Deauthenticates users."""
    logout_user()
    flash("Logged Out", category="success")
    return redirect(url_for("auth_bp.login"))


@auth_bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    """Updates users information."""
    admin_form = AdminForm()
    if request.method == "POST" and admin_form.validate():
        user = User.query.filter_by(username=current_user.username).first()
        user.username = admin_form.username.data
        user.password = generate_password_hash(admin_form.password.data)
        db.session.commit()
        flash("User Details Updated", category="success")
        return redirect(url_for("auth_bp.admin"))
    return render_template("auth/admin.html",
                           user=current_user,
                           admin_form=admin_form)
