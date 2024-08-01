"""All functions required for scheduling and executing water process."""
from app.water.models import Plant, History
from app import db, scheduler, events
from datetime import timedelta, datetime
from suntime import Sun
import openmeteo_requests
import time
import pytz


def get_sun_tz():
    """Creates and returns a sun and timezone object based on app config."""
    sun = Sun(scheduler.app.config["LATITUDE"], scheduler.app.config["LONGITUDE"])
    tz = pytz.timezone(scheduler.app.config["TIMEZONE"])
    return sun, tz


def get_due_date(config):
    """Gets the due date for scheduling the water process.

    Adds the value of occurrence_days to current date where the time is
    then replaced with the corresponding sunrise, sunset, or default value.

    Args:
        config: An entry in the config table for a plant.

    Returns:
        A datetime object.
    """
    due = datetime.now().replace(microsecond=0) + timedelta(days=config.occurrence_days)
    if config.mode == 1:
        sun, tz = get_sun_tz()
        sunset = sun.get_sunset_time(due, tz).time()
        due = due.replace(hour=sunset.hour, minute=sunset.minute, second=sunset.second)
    elif config.mode == 2:
        sun, tz = get_sun_tz()
        sunrise = sun.get_sunrise_time(due, tz).time()
        due = due.replace(hour=sunrise.hour, minute=sunrise.minute, second=sunrise.second)
    else:
        default = config.default
        due = due.replace(hour=default.hour, minute=default.minute, second=default.second)
    return due


def remove_job(plant_id):
    """Removes job auto_water from scheduler for the given plant."""
    job = f"auto_water{plant_id}"
    if scheduler.get_job(job):
        scheduler.remove_job(job)
    return


def schedule_job(plant):
    """Adds job auto_water to scheduler for the given plant."""
    job_name = f"auto_water{plant.id}"
    scheduler.add_job(func=auto_water,
                      trigger="date",
                      run_date=plant.config.job_due,
                      id=job_name,
                      name=job_name,
                      args=[plant.id])
    return


def auto_water(plant_id):
    """Function used by scheduler for automatic execution of water process.

    Executes water process only if rain_reset is enabled in the plants config
    and check_rain returns true. This job is then added back to the scheduler
    under the same name and id for a new due date.

    Args:
        plant_id: The id assigned to an entry in the plant table.
    """
    with scheduler.app.app_context():
        plant = Plant.query.filter(Plant.id == plant_id).first()
        if not plant.config.rain_reset or not check_rain(plant.config):
            process(plant.config.duration_sec, plant.id)
        now = datetime.now().replace(microsecond=0)
        plant.config.job_init = now
        plant.config.job_due = get_due_date(plant.config)
        schedule_job(plant)
        db.session.commit()
    return


def check_rain(config):
    """Returns true if rainfall meets threshold.

    Move url to config, redo weather with this api
    as its far more suitable.

    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": scheduler.app.config["LATITUDE"],
        "longitude": scheduler.app.config["LONGITUDE"],
        "daily": "precipitation_sum",
        "timezone": scheduler.app.config["TIMEZONE"],
        "start_date": config.job_init.date(),
        "end_date": config.job_due.date()
    }
    om = openmeteo_requests.Client()
    responses = om.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()
    rain_sum = sum(daily.Variables(0).ValuesAsNumpy())
    if rain_sum >= config.threshold_mm:
        return True
    else:
        return False


def process(duration_sec, plant_id):
    """Water process."""
    with scheduler.app.app_context():
        plant_selected = Plant.query.filter(Plant.id == plant_id).first()
        plant_selected.status = True
        plant_selected.history.append(History(start_date_time=datetime.now(), duration_sec=duration_sec))
        db.session.commit()
        scheduler.app.logger.debug(f"Set status of '{plant_selected.name}' to {plant_selected.status}")
        scheduler.app.logger.debug(f"Watering '{plant_selected.name}' for {duration_sec} seconds")
        event = events[plant_selected.name]
        plant_selected.system.obj.on()
        loop(duration_sec, event)
        plant_selected.system.obj.off()
        plant_selected.status = False
        db.session.commit()
        scheduler.app.logger.debug(f"Set status of '{plant_selected.name}' to {plant_selected.status}")
        scheduler.app.logger.debug(f"Finished watering process for '{plant_selected.name}'")
    return


def loop(duration_sec, event):
    """Inner loop of water process."""
    scheduler.app.logger.debug("Loop started")
    for x in range(duration_sec):
        time.sleep(1)
        if event.is_set():
            scheduler.app.logger.debug("Loop cancelled")
            event.clear()
            return
    scheduler.app.logger.debug("Loop stopped")
    return
