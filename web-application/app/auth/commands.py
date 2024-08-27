"""Click commands used by flask application."""
import click
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.auth.models import User


@click.command()
@click.argument("username")
@click.argument("password")
def create_user(username, password):
    """Creates user accounts."""
    user = User.query.filter_by(username=username).first()
    if user:
        print("Error")
    else:
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()


@click.command()
@click.argument("username")
@click.argument("password")
def drop_user(username, password):
    """Deletes user accounts."""
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        db.session.delete(user)
        db.session.commit()
    else:
        print("Error")
