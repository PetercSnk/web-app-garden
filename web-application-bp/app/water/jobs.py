from app.water.models import Plant, History
import time
from app import db, scheduler, events
import pytz
import openmeteo_requests
from datetime import timedelta, datetime
from suntime import Sun
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR


def get_sun_tz():
    """Return sun and timezone object."""
    sun = Sun(scheduler.app.config["LATITUDE"], scheduler.app.config["LONGITUDE"])
    tz = pytz.timezone(scheduler.app.config["TIMEZONE"])
    return sun, tz


def get_estimate(config):
    """Get the next earliest estimate for watering."""
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


def log_active_jobs():
    jobs = scheduler.get_jobs()
    for job in jobs:
        scheduler.app.logger.debug(f"Active job '{job.name}' scheduled for {job.next_run_time}")
    return


def remove_job(plant):
    """Remove existing jobs."""
    job_name = f"plant_{plant.id}"
    if scheduler.get_job(job_name):
        scheduler.remove_job(job_name)
        scheduler.app.logger.debug(f"Removed job '{job_name}'")
    return


def add_job(plant):
    job_name = f"plant_{plant.id}"
    scheduler.add_job(func=task,
                      trigger="date",
                      run_date=plant.config.estimate,
                      id=job_name,
                      name=job_name,
                      args=[job_name])
    scheduler.app.logger.debug(f"Added job for {plant.name}")
    return


def task(arg):
    scheduler.app.logger.debug(f"RUNNING JOB {arg}")
    return


def check_rain(plant):
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
        "start_date": plant.config.last_edit.date(),
        "end_date": plant.config.estimate.date()
    }
    om = openmeteo_requests.Client()
    responses = om.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()
    rain_sum = sum(daily.Variables(0).ValuesAsNumpy())
    if rain_sum >= plant.config.threshold_mm:
        return True
    else:
        return False


"""TODO
func to add job @ estimated date
func to check if rain
reschedule job if rains
only start job if config enabled
stop job if disabled
start all jobs on restart using estimate in db and if config enabled
"""


def process(app, duration_sec, plant_id):
    """Watering process."""
    with app.app_context():
        plant_selected = Plant.query.filter(Plant.id == plant_id).first()
        plant_selected.status = True
        plant_selected.history.append(History(start_date_time=datetime.now(), duration_sec=duration_sec))
        db.session.commit()
        app.logger.debug(f"Set status of '{plant_selected.name}' to {plant_selected.status}")
        app.logger.info(f"Watering '{plant_selected.name}' for {duration_sec} seconds")
        event = events[plant_selected.name]
        plant_selected.system.obj.on()
        loop(app, duration_sec, event)
        plant_selected.system.obj.off()
        plant_selected.status = False
        db.session.commit()
        app.logger.debug(f"Set status of '{plant_selected.name}' to {plant_selected.status}")
        app.logger.debug(f"Finished watering process for '{plant_selected.name}'")
    return


def loop(app, duration_sec, event):
    """Inner loop of watering process."""
    app.logger.debug("Loop started")
    for x in range(duration_sec):
        time.sleep(1)
        if event.is_set():
            app.logger.debug("Loop cancelled")
            event.clear()
            return
    app.logger.debug("Loop stopped")
    return


def listener_callback(event):
    with scheduler.app.app_context():
        print(event)


scheduler.add_listener(listener_callback, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
