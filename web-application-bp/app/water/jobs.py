from app.water.models import Plant
from app import db, scheduler
import pytz
import openmeteo_requests
from datetime import timedelta
from suntime import Sun


def get_sun_tz():
    """Return sun and timezone object."""
    sun = Sun(scheduler.app.config["LATITUDE"], scheduler.app.config["LONGITUDE"])
    tz = pytz.timezone(scheduler.app.config["TIMEZONE"])
    return sun, tz


def get_estimate(config):
    """Get the next earliest estimate for watering."""
    #start = config.last_edit.replace(hour=0, minute=0, second=0, microsecond=0)
    estimate = config.last_edit + timedelta(days=config.occurrence_days)
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
    pass


def _job(plant_id):
    rain = check_rain(plant_id)
    scheduler.app.logger.debug(rain)
    return rain


def check_rain(plant_id):
    """Returns true if rainfall meets threshold"""
    plant_selected = Plant.query.filter(Plant.id == plant_id).first()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": scheduler.app.config["LATITUDE"],
        "longitude": scheduler.app.config["LONGITUDE"],
        "daily": "precipitation_sum",
        "timezone": scheduler.app.config["TIMEZONE"],
        "start_date": plant_selected.config.last_edit.date(),
        "end_date": plant_selected.config.estimate.date()
    }
    om = openmeteo_requests.Client()
    responses = om.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()
    rain_sum = sum(daily.Variables(0).ValuesAsNumpy())
    if rain_sum >= plant_selected.config.threshold_mm:
        return True
    else:
        return False


# move process and inner loop here so scheduler can use it
# move update of db from water func to process
# is db.session.commit() needed in water, is setting the status to true enough to show on page
"""TODO
add estimate to plant db
func to add job @ estimated date
func to check if rain
reschedule job if rains
only start job if config enabled
stop job if disabled
start all jobs on restart using estimate in db and if config enabled
"""
