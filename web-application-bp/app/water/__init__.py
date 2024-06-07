from flask import Blueprint

water_bp = Blueprint("water_bp", __name__, template_folder="templates", static_folder="core/static")

from app.water import water
