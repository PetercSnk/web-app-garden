from app.weather.models import Weather, Day
from app import db
from app.core.extensions import scheduler
import datetime
from suntime import Sun
import requests
from app.weather.config import Config


@scheduler.task("cron", id="get_weather", minute="0", hour="1", day="*", month="*", day_of_week="*")
def get_weather():
    status, reason, ok, json = request_weather()
    if ok:
        organised_forecast = remove_missing(extract_data(json))
        dates_added = add_to_db(organised_forecast)
        if dates_added:
            return "Added: " + ", ".join(dates_added)
        else:
            return "No New Data"
    else:
        scheduler.app.logger.error(status)
        scheduler.app.logger.error(reason)
        scheduler.app.logger.error(json)
        return "Error"


def kelvin_to_celsius(kelvin):
    return (kelvin - 273.15)


def request_weather():
    LAT = "51.529"
    LON = "-3.191"
    url = Config.BASE_URL + "lat=" + LAT + "&lon=" + LON + "&appid=" + Config.API_KEY
    request = requests.get(url)
    return request.status_code, request.reason, request.ok, request.json()


def extract_data(json):
    # information about city
    city = json["city"]
    latitude = city["coord"]["lat"]
    longitude = city["coord"]["lon"]
    timedelta = datetime.timedelta(seconds=city["timezone"])
    timezone = datetime.timezone(timedelta)
    # extract and organise only the necessary data
    organised_forecast = {}
    five_day_forecast = json["list"]
    for three_hour_step in five_day_forecast:
        date_time = datetime.datetime.utcfromtimestamp(three_hour_step["dt"]).astimezone(timezone)
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
        # date is used as key within organised_forecast, its value is another dictionary containing a list of three hourly weather data, and the time of sunrise and sunset for that day
        date = date_time.date()
        if date in organised_forecast:
            organised_forecast[date]["weather_data"].append(weather_data)
        else:
            sun = Sun(latitude, longitude)
            organised_forecast[date] = {"weather_data": [weather_data], "sunrise": sun.get_sunrise_time(date_time, timezone).time(), "sunset": sun.get_sunset_time(date_time, timezone).time()}
    return organised_forecast


def remove_missing(organised_forecast):
    # remove entries that have missing data, for some reason openweathermap include a 6th day in a 5 day forecast which has missing data
    items_to_remove = []
    for date, data in organised_forecast.items():
        if len(data["weather_data"]) < 8:
            items_to_remove.append(date)
    for item in items_to_remove:
        organised_forecast.pop(item)
    return organised_forecast


def add_to_db(organised_forecast):
    with scheduler.app.app_context():
        db_dates = [day.date for day in Day.query.order_by(Day.date).all()]
        dates_added = []
        for date, data in organised_forecast.items():
            if date not in db_dates:
                day = Day(date=date, sunrise=data["sunrise"], sunset=data["sunset"])
                dates_added.append(date.strftime("%d/%m/%y"))
                for weather_data in data["weather_data"]:
                    weather = Weather(time=weather_data["time"], temperature_c=weather_data["temperature_c"], humidity=weather_data["humidity"], description=weather_data["description"], rain_probability=weather_data["rain_probability"], rain_volume_mm=weather_data["rain_volume_mm"])
                    day.weather.append(weather)
                db.session.add(day)
        db.session.commit()
    return dates_added


@scheduler.task("cron", id="delete_old_records", minute="0", hour="2", day="*", month="*", day_of_week="*")
def delete_old_records():
    with scheduler.app.app_context():
        db_days = Day.query.order_by(Day.date).all()
        # keeps data for only 7 days
        days_to_delete = db_days[:-7]
        if days_to_delete:
            for day in days_to_delete:
                db.session.delete(day)
            db.session.commit()
        return
