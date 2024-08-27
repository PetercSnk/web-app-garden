"""Blueprint and initialisation of core module."""
from flask import Blueprint

core_bp = Blueprint("core_bp",
                    __name__,
                    template_folder="templates",
                    static_folder="static",
                    static_url_path="/core/static")

from app.core import core
