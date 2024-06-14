from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()


def create_app():
    # create and configure flask instance
    app = Flask(__name__)
    from app.core.config import Config
    app.config.from_object(Config)

    # initialise databases
    db.init_app(app)

    # initialise extensions
    from app.core import extensions
    extensions.executor.init_app(app)
    extensions.scheduler.init_app(app)
    extensions.scheduler.start()

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
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # weather module setup
    from app.weather import weather_bp, jobs
    app.register_blueprint(weather_bp, url_prefix="/weather")

    # water module setup
    from app.water import water_bp
    app.register_blueprint(water_bp, url_prefix="/water")
    water_status = False
    # from app.water.models import WaterStatus
    #     # REPLACE WITH JUST A VARIABLE AND IMPORT?? EASIER THAN DB
    #     water_status = WaterStatus.query.first()
    #     if not water_status:
    #         db.session.add(WaterStatus(status=False))
    #         db.session.commit()
    #     # incase of restart during water
    #     water_status = WaterStatus.query.one()
    #     water_status.status = False
    #     db.session.commit()

    # command for creating a user account
    # MAKE THIS A REGISTER PAGE INSTEAD OF COMMAND

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
