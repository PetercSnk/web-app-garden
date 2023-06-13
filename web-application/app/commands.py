from werkzeug.security import generate_password_hash
from .models import db, User
import click

@click.command()
@click.argument("username")
@click.argument("password")
def create_user(username, password):
    """Create user account."""
    initialUser = User(username=username, password=generate_password_hash(password, method="sha256"))
    db.session.add(initialUser)
    db.session.commit()