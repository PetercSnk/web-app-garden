"""Click commands used by flask application."""
import click
from app import db
from app.weather.models import Daily


@click.command()
@click.argument("day_id")
def drop_day(day_id):
    """Deletes specific day entries for a given id."""
    day = Daily.query.filter_by(id=day_id).first()
    if day:
        db.session.delete(day)
        db.session.commit()
    else:
        print(f"Daily with id '{day_id}' does not exist")


@click.command()
def drop_all_days():
    """Deletes all day entries in day table."""
    days = Daily.query.all()
    for day in days:
        db.session.delete(day)
    db.session.commit()
