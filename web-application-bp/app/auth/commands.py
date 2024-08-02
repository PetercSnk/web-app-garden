"""Click commands used by flask application."""
import click
from werkzeug.security import generate_password_hash
from app import db
from app.auth.models import User


@click.command()
@click.argument("username")
@click.argument("password")
def create_user(username, password):
    """Creates user accounts."""
    user = User(username=username, password=generate_password_hash(password, method="sha256"))
    db.session.add(user)
    db.session.commit()
