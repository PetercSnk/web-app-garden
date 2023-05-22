from flask import Flask
import click
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

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
    
    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument("password")
    def createUser(username, password):
        initialUser = User(username=username, password=generate_password_hash(password, method="sha256"))
        db.session.add(initialUser)
        db.session.commit()
    app.cli.add_command(createUser)

    return app
