from app import db, scheduler
from app.weather.models import Day
from datetime import datetime


def reschedule():
    today = datetime.now().date()
    day = Day.query.filter(Day.date == today).first()
    if day:
        sunrise = day.sunrise
        sunset = day.sunset
        x = day.weather.rain_probability
        y = day.weather.rain_volume_mm
        with scheduler.app.app_context():
            scheduler.app.logger.debug(f"x:{x}, y:{y}, s{sunrise, sunset}")
