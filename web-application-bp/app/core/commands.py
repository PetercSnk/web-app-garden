from app import db
import click


@click.command()
def drop_db():
    """Delete databases."""
    db.drop_all()
