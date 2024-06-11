from flask import redirect, url_for
from app.core import core_bp


@core_bp.route("/", methods=["GET"])
def core_index():
    return redirect(url_for("auth_bp.login"))
