"""Click commands used by flask application."""
import click
from app import db


@click.command()
def drop_db():
    """Deletes all databases."""
    db.drop_all()
