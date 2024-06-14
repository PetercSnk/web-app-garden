from app import db
import click


@click.command()
def init_db():
    """Create databases"""
    db.create_all()


@click.command()
def drop_db():
    """Delete databases"""
    db.drop_all()
