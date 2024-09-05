"""Flask application factory."""
import os
from logging.config import dictConfig
import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler

# Required application extensions.
# These should ideally be in some other extension file.
db = SQLAlchemy()
login_manager = LoginManager()
scheduler = APScheduler()
events = {}


def create_app():
    """Creates and returns the flask application."""
    # Sets up the logging config before creating the application object.
    basedir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(basedir, "core", "logging.yaml")
    with open(path, "rt") as f:
        logging_config = yaml.safe_load(f.read())
    dictConfig(logging_config)

    # Creates the flask application object and loads config.
    app = Flask(__name__)
    from app.core.config import Config
    app.config.from_object(Config)

    # Initialises and creates all databases.
    db.init_app(app)
    from app.auth.models import User
    from app.weather.models import Daily, Hourly
    from app.water.models import System, Plant, History, Config
    with app.app_context():
        db.create_all()

    # Initialises the scheduler.
    scheduler.init_app(app)
    scheduler.start()

    # Core module setup.
    from app.core import core_bp
    app.register_blueprint(core_bp)
    from app.core import commands as core_cmds
    app.cli.add_command(core_cmds.drop_db)

    # Auth module setup.
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from app.auth import commands as auth_cmds
    app.cli.add_command(auth_cmds.create_user)
    app.cli.add_command(auth_cmds.drop_user)
    login_manager.login_view = "auth_bp.login"
    login_manager.login_message = "Please Login"
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Weather module setup.
    from app.weather import weather_bp
    app.register_blueprint(weather_bp, url_prefix="/weather")
    from app.weather import commands as weather_cmds
    app.cli.add_command(weather_cmds.drop_day)
    app.cli.add_command(weather_cmds.drop_all_days)

    # Water module setup.
    from app.water import water_bp
    app.register_blueprint(water_bp, url_prefix="/water")
    from app.water.setup import init_systems, init_plants
    with app.app_context():
        init_systems()
        init_plants()

    # Returns the flask application object.
    return app
