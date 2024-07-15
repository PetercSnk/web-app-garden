from app.weather.models import Weather, Day
from app import db, scheduler
from datetime import datetime
from suntime import Sun
import requests
import traceback
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import pytz


@scheduler.task("cron", id="get_weather", minute="0", hour="1", day="*", month="*", day_of_week="*")
def get_weather():
    ok, json = request_weather()
    if ok:
        organised_forecast = extract_data(json)
        if organised_forecast:
            dates_added = add_to_db(remove_missing(organised_forecast))
            if dates_added:
                return "Added: " + ", ".join(dates_added)
            else:
                return "No new data"
        else:
            return "Error"
    else:
        return "Error"


def kelvin_to_celsius(kelvin):
    return (kelvin - 273.15)


def request_weather():
    try:
        config = scheduler.app.config
        url = f"{config['BASE_URL']}lat={config['LATITUDE']}&lon={config['LONGITUDE']}&appid={config['API_KEY']}"
        request = requests.get(url)
        scheduler.app.logger.debug(f"Request made to {url}")
        json = request.json()
        request.raise_for_status()
    except Exception as error:
        scheduler.app.logger.error(f"A {type(error).__name__} has occured | {request.status_code} {request.reason} | Response {json}")
    return request.ok, json


def extract_data(json):
    try:
        organised_forecast = {}
        timezone = pytz.timezone(scheduler.app.config["TIMEZONE"])
        five_day_forecast = json["list"]
        for three_hour_step in five_day_forecast:
            date_time = datetime.utcfromtimestamp(three_hour_step["dt"])
            weather_data = {
                "time": date_time.time(),
                "temperature_c": round(kelvin_to_celsius(three_hour_step["main"]["temp"]), 2),
                "humidity": three_hour_step["main"]["humidity"],
                "description": three_hour_step["weather"][0]["description"],
                "rain_probability": three_hour_step["pop"]
            }
            # the volume of rain fall is not always included, check it exists or set it to zero
            if "rain" in three_hour_step:
                weather_data["rain_volume_mm"] = three_hour_step["rain"]["3h"]
            else:
                weather_data["rain_volume_mm"] = 0
            # store all three houlry weather data, sunrise, and sunset for its date in organised forecast
            date = date_time.date()
            if date in organised_forecast:
                organised_forecast[date]["weather_data"].append(weather_data)
            else:
                sun = Sun(scheduler.app.config["LATITUDE"], scheduler.app.config["LONGITUDE"])
                organised_forecast[date] = {"weather_data": [weather_data], "sunrise": sun.get_sunrise_time(date_time, timezone).time(), "sunset": sun.get_sunset_time(date_time, timezone).time()}
        return organised_forecast
    except Exception as error:
        scheduler.app.logger.error(f"A {type(error).__name__} has occured | {traceback.format_exc()}")
        return {}


def remove_missing(organised_forecast):
    # remove entries that have missing data, for some reason openweathermap include a 6th day in a 5 day forecast which has missing data
    remove = []
    remove_log = []
    for date, data in organised_forecast.items():
        if len(data["weather_data"]) < 8:
            remove.append(date)
            remove_log.append(date.strftime("%d/%m/%y"))
    for date in remove:
        organised_forecast.pop(date)
    scheduler.app.logger.debug(f"Dates {remove_log} contain missing data, removing")
    return organised_forecast


def add_to_db(organised_forecast):
    with scheduler.app.app_context():
        dates = [day.date for day in Day.query.order_by(Day.date).all()]
        add_log = []
        exists_log = []
        for date, data in organised_forecast.items():
            if date not in dates:
                day = Day(date=date, sunrise=data["sunrise"], sunset=data["sunset"])
                add_log.append(date.strftime("%d/%m/%y"))
                for weather_data in data["weather_data"]:
                    weather = Weather(time=weather_data["time"], temperature_c=weather_data["temperature_c"], humidity=weather_data["humidity"], description=weather_data["description"], rain_probability=weather_data["rain_probability"], rain_volume_mm=weather_data["rain_volume_mm"])
                    day.weather.append(weather)
                db.session.add(day)
            else:
                exists_log.append(date.strftime("%d/%m/%y"))
        db.session.commit()
    scheduler.app.logger.debug(f"Dates {exists_log} already exist in database")
    scheduler.app.logger.debug(f"Dates {add_log} added to database")
    return add_log


@scheduler.task("cron", id="delete_old_records", minute="30", hour="1", day="*", month="*", day_of_week="*")
def delete_old_records():
    with scheduler.app.app_context():
        days = Day.query.order_by(Day.date).all()
        # keeps data for only 7 days
        delete = days[:-7]
        delete_log = []
        if delete:
            for day in delete:
                delete_log.append(day.date.strftime("%d/%m/%y"))
                db.session.delete(day)
            db.session.commit()
    scheduler.app.logger.debug(f"Deleted {delete_log} from database")
    return


def listener_callback(event):
    with scheduler.app.app_context():
        print(event)


scheduler.add_listener(listener_callback, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
