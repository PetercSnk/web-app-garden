"""All functions required for scheduling and executing the watering process."""
import time
from datetime import timedelta, datetime
import pytz
import openmeteo_requests
from astral import LocationInfo
from astral.sun import sun
from app.water.models import Plant, History
from app import db, scheduler, events


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
    city = LocationInfo(scheduler.app.config["CITY"],
                        scheduler.app.config["REGION"],
                        scheduler.app.config["TIMEZONE"],
                        scheduler.app.config["LATITUDE"],
                        scheduler.app.config["LONGITUDE"])
    tz = pytz.timezone(scheduler.app.config["TIMEZONE"])
    s = sun(city.observer, tzinfo=tz, date=due)
    if config.mode == 1:
        sunset = s["sunset"].time()
        due = due.replace(hour=sunset.hour, minute=sunset.minute, second=sunset.second)
    elif config.mode == 2:
        sunrise = s["sunrise"].time()
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
    and check_rain returns true, otherwise the watering process always executes. The
    plants config is updated where this job is scheduled again for the new due date.

    Args:
        plant_id: Unique id given to a plant.
    """
    with scheduler.app.app_context():
        plant = Plant.query.filter(Plant.id == plant_id).first()
        # Checks plants statuses are false so the manual and automatic watering processes don't overlap.
        # Also ensures the process only executes when rain reset is disabled or the threshold isn't met.
        if not plant.status and (not plant.config.rain_reset or not check_rain(plant.config)):
            process(plant.config.duration_sec, plant.id)
        else:
            scheduler.app.logger.info("Rain reset and threshold met or attempt to execute job when already running")
        plant.config.job_init = datetime.now().replace(microsecond=0)
        plant.config.job_due = get_due_date(plant.config)
        schedule_job(plant)
        db.session.commit()
    return


def check_rain(config):
    """Returns true if rainfall meets the threshold specified within the config."""
    url = scheduler.app.config["URL"]
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

    Enables the system object assigned to the plant and sleeps for the duration
    specified. After the duration or upon an event update the system object is
    disabled. The plant status is updated alongside the system object to ensure
    the process cannot run in multiple instances

    Args:
        duration_sec: An integer refering to a time in seconds.
        plant_id: Unique id given to a plant.
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
    """The inner loop used to sleep by the watering process."""
    scheduler.app.logger.debug("Loop started")
    for x in range(duration_sec):
        time.sleep(1)
        if event.is_set():
            scheduler.app.logger.debug("Loop cancelled")
            event.clear()
            return
    scheduler.app.logger.debug("Loop stopped")
    return
