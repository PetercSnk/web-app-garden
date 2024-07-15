from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler
import logging.config
import os
import yaml


db = SQLAlchemy()
login_manager = LoginManager()
scheduler = APScheduler()
events = {}


def create_app():
    # setup logging config before creating application object
    basedir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(basedir, "core", "logging.yaml")
    with open(path, "rt") as f:
        logging_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logging_config)

    # create and configure flask instance
    app = Flask(__name__)
    from app.core.config import Config
    app.config.from_object(Config)

    # set the applications logger
    if app.debug:
        app.logger = logging.getLogger("development")

    # initialise databases
    db.init_app(app)

    # initialise scheduler
    scheduler.init_app(app)
    scheduler.start()

    # core module setup
    from app.core import core_bp
    app.register_blueprint(core_bp)
    from app.core import commands as core_cmds
    app.cli.add_command(core_cmds.init_db)
    app.cli.add_command(core_cmds.drop_db)

    # auth module setup
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from app.auth import commands as auth_cmds
    app.cli.add_command(auth_cmds.create_user)
    from app.auth.models import User
    login_manager.login_view = "auth_bp.login"
    login_manager.login_message = "Please login"
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # weather module setup
    from app.weather import weather_bp
    app.register_blueprint(weather_bp, url_prefix="/weather")
    from app.weather import commands as weather_cmds
    app.cli.add_command(weather_cmds.drop_day)
    app.cli.add_command(weather_cmds.drop_all_days)

    # water module setup
    from app.water import water_bp
    app.register_blueprint(water_bp, url_prefix="/water")
    from app.water.setup import init_systems, init_plants
    with app.app_context():
        init_systems()
        init_plants()
    return app
