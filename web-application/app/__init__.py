from flask import Flask
from .config import Config
from flask_login import LoginManager
from flask_executor import Executor
from flask_apscheduler import APScheduler

executor = Executor()
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .models import db, User, WaterStatus
    db.init_app(app)

    executor.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    from .routes import routes
    from .auth import auth
    app.register_blueprint(routes, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    
    with app.app_context():
        db.create_all()
        # incase of restart during water
        water_status = WaterStatus.query.first()
        water_status.status = False
        db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    from . import commands
    app.cli.add_command(commands.create_user)

    # incase of restart during water
    from .pump import Pump
    from .valve import Valve
    pump_relay = 16
    valve_relay = 18
    valve_switch = 12
    valve = Valve(valve_relay, valve_switch)
    pump = Pump(pump_relay)
    valve.valve_off()
    pump.pump_off()

    return app
