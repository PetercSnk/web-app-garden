"""All functions required for scheduling and executing the watering process."""
from app.water.models import Plant, History
from app import db, scheduler, events
from datetime import timedelta, datetime
from suntime import Sun
import openmeteo_requests
import time
import pytz


def get_sun_tz():
    """Creates and returns a sun and timezone object based on the flask config."""
    sun = Sun(scheduler.app.config["LATITUDE"], scheduler.app.config["LONGITUDE"])
    tz = pytz.timezone(scheduler.app.config["TIMEZONE"])
    return sun, tz


def get_due_date(config):
    """Retrieves the date to be used when scheduling the automated watering process.

    Converts the value of occurence_days within config to a datetime object which is then
    added to the current date. This date then has its time replaced with the corresponding
    sunrise, sunset, or default value.

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
    """Removes the job auto_water from the scheduler for the given plant."""
    job = f"auto_water{plant_id}"
    if scheduler.get_job(job):
        scheduler.remove_job(job)
    return


def schedule_job(plant):
    """Adds the job auto_water to the scheduler for the given plant."""
    job_name = f"auto_water{plant.id}"
    scheduler.add_job(func=auto_water,
                      trigger="date",
                      run_date=plant.config.job_due,
                      id=job_name,
                      name=job_name,
                      args=[plant.id])
    return


def auto_water(plant_id):
    """Function used by the scheduler for automatic execution of the watering process.

    The watering process is only skipped when rain_reset is enabled in the plants config
    and check_rain returns true, otherwise the watering process always executes. The values
    for job_init and job_due are then updated in the plants config where this job is
    scheduled again for the new due date.

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
    """Returns true if rainfall meets the threshold specified within the config.

    TODO:
        Move url to config, redo weather with this api as its far more suitable.

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
    """Enables and disables system objects for a time in seconds.

    The status of the plant is set to true and an entry is added into the history table. The
    system object assigned to the plant is then enabled where operations halt for the duration.
    The inner loop used during the halt can be cancelled using the corresponding event. After
    the duration the system object is turned off and the status of the plant is set to false.

    Args:
        duration_sec: An integer refering to a time in seconds.
        plant_id: The id assigned to an entry in the plant table.
    """
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
    """The inner loop used to halt operations by the watering process."""
    scheduler.app.logger.debug("Loop started")
    for x in range(duration_sec):
        time.sleep(1)
        if event.is_set():
            scheduler.app.logger.debug("Loop cancelled")
            event.clear()
            return
    scheduler.app.logger.debug("Loop stopped")
    return
