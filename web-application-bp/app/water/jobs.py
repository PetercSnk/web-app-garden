from app.water.models import Plant
from app import db, scheduler
import pytz
from datetime import datetime, timedelta
from suntime import Sun


def get_sun_tz():
    """Return sun and timezone object."""
    sun = Sun(scheduler.app.config["LATITUDE"], scheduler.app.config["LONGITUDE"])
    tz = pytz.timezone(scheduler.app.config["TIMEZONE"])
    return sun, tz


def get_next_estimate(config):
    """Get the next earliest estimate for watering."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    estimate = today + timedelta(days=config.occurrence_days)
    if config.mode == 1:
        sun, tz = get_sun_tz()
        sunset = sun.get_sunset_time(estimate, tz).time()
        estimate = estimate.replace(hour=sunset.hour, minute=sunset.minute, second=sunset.second)
    elif config.mode == 2:
        sun, tz = get_sun_tz()
        sunrise = sun.get_sunrise_time(estimate, tz).time()
        estimate = estimate.replace(hour=sunrise.hour, minute=sunrise.minute, second=sunrise.second)
    else:
        default = config.default
        estimate = estimate.replace(hour=default.hour, minute=default.minute, second=default.second)
    return estimate


# run on date of water, check weather if enabled, check sun, create job for water
def add_job(plant_id):
    scheduler.app.logger.debug(f"run rescheduler for {plant_id}")


"""TODO
add estimate to plant db
func to add job @ estimated date
func to check if rain
reschedule job if rains
only start job if config enabled
stop job if disabled
start all jobs on restart using estimate in db and if config enabled
"""
