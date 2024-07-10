from flask import Blueprint

"""Blueprint for water module."""
water_bp = Blueprint("water_bp", __name__, template_folder="templates", static_folder="static", static_url_path="water/static")

from app.water import water
