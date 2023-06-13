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

    from .models import db
    db.init_app(app)

    executor.init_app(app)

    scheduler.init_app(app)
    scheduler.start()

    from .routes import routes
    from .auth import auth

    app.register_blueprint(routes, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    from . import commands
    app.cli.add_command(commands.create_user)

    return app
