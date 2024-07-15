from app.water.models import Plant
from app import scheduler
import pytz
from datetime import datetime, timedelta, timezone, date, time
from suntime import Sun


# schedule rescheduler
def get_next_estimate(plant_id):
    plant_selected = Plant.query.filter(Plant.id == plant_id).first()
    today = datetime.combine(date.today(), time())
    estimate = today + timedelta(days=plant_selected.config.occurrence_days)
    scheduler.app.logger.debug(estimate)
    scheduler.app.logger.debug(type(estimate))
    sun = Sun(scheduler.app.config["LATITUDE"], scheduler.app.config["LONGITUDE"])
    tz = pytz.timezone(scheduler.app.config["TIMEZONE"])
    if plant_selected.config.mode == 1:
        sunset = sun.get_sunset_time(today, tz).time()
        scheduler.app.logger.debug(sunset.minute)
        estimate.replace(hour=sunset.hour, minute=sunset.minute, second=sunset.second)
    elif plant_selected.config.mode == 2:
        sunrise = sun.get_sunrise_time(today, tz).time()
        estimate.replace(hour=sunrise.hour, minute=sunrise.minute, second=sunrise.second)
    else:
        default = plant_selected.config.default
        estimate.replace(hour=default.hour, minute=default.minute, second=default.second)
    return estimate


# run on date of water, check weather if enabled, check sun, create job for water
def rescheduler(plant_id):
    scheduler.app.logger.debug(f"run rescheduler for {plant_id}")



"""add job creates job for estimated day, resch only checks if rain
if yes run add job again"""
