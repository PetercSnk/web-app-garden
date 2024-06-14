from flask import redirect, url_for
from flask_login import current_user
from app.core import core_bp


@core_bp.route("/", methods=["GET"])
def core_index():
    if current_user.is_authenticated:
        return redirect(url_for("weather_bp.index"))
    else:
        return redirect(url_for("auth_bp.login"))
