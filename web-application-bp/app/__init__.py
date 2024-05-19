from flask import Flask
from flask_login import LoginManager
# import executor and scheduler
from app.core import extensions
# import blueprints
from app.core import core
from app.auth import auth_bp
from app.water import water_bp
from app.weather import weather_bp
# import app config
from app.core.config import Config
# import db
from app.core.models import db, User, WaterStatus
# import useful commands
from app.core import commands
# import jobs
from app.core import jobs


def create_app():
    # create app instance
    app = Flask(__name__)
    # load config from obj
    app.config.from_object(Config)
    # register blueprints
    app.register_blueprint(core)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(water_bp, url_prefix="/water")
    app.register_blueprint(weather_bp, url_prefix="/weather")
    # initialise executor and scheduler
    extensions.executor.init_app(app)
    extensions.scheduler.init_app(app)
    extensions.scheduler.start()
    # create login manager instance
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # required to check user is authenticated
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # create database instance
    db.init_app(app)
    # create tables based on models
    with app.app_context():
        db.create_all()
        # REPLACE WITH JUST A VARIABLE AND IMPORT?? EASIER THAN DB
        water_status = WaterStatus.query.one()
        if not water_status:
            db.session.add(WaterStatus(status=False))
            db.session.commit()
        # incase of restart during water
        water_status = WaterStatus.query.one()
        water_status.status = False
        db.session.commit()

    # command for creating a user account
    # MAKE THIS A REGISTER PAGE INSTEAD OF COMMAND
    app.cli.add_command(commands.create_user)

    # from .pump import Pump
    # from .valve import Valve
    # pump_relay = 16
    # valve_relay = 18
    # valve_switch = 12
    # valve = Valve(valve_relay, valve_switch)
    # pump = Pump(pump_relay)
    # valve.valve_off()
    # pump.pump_off()

    return app
