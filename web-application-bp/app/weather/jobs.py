"""All functions required for scheduling the retrieval of weather data."""
from datetime import datetime
import requests
import traceback
import pytz
import openmeteo_requests
import pandas as pd
import numpy as np
from suntime import Sun
from app.weather.models import Weather, Day
from app import db, scheduler


@scheduler.task("cron", id="get_weather", minute="0", hour="1", day="*", month="*", day_of_week="*")
def get_weather():
    response = get_response()
    daily_dataframe, hourly_dataframe = format_response(response)
    daily_dataframe = add_sun(daily_dataframe)
    #insert_into_db(daily_dataframe, hourly_dataframe)
    print(daily_dataframe)
    print(hourly_dataframe)


def get_response():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": scheduler.app.config["LATITUDE"],
        "longitude": scheduler.app.config["LONGITUDE"],
        "hourly": ["temperature_2m",
                   "relative_humidity_2m",
                   "precipitation_probability",
                   "precipitation"],
        "daily": "weather_code",
        "timezone": scheduler.app.config["TIMEZONE"],
        "past_days": 3
    }
    om = openmeteo_requests.Client()
    responses = om.weather_api(url, params=params)
    response = responses[0]
    return response


def format_response(response):
    hourly = response.Hourly()
    hourly_temperature = hourly.Variables(0).ValuesAsNumpy()
    hourly_humidity = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()
    hourly_datetime_dataframe = pd.DataFrame({"datetime": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )})
    hourly_data = {
        "date": pd.to_datetime(hourly_datetime_dataframe["datetime"]).dt.date,
        "time": pd.to_datetime(hourly_datetime_dataframe["datetime"]).dt.time,
        "temperature": hourly_temperature,
        "humidity": hourly_humidity,
        "precipitation_probability": hourly_precipitation_probability,
        "precipitation": hourly_precipitation
    }
    hourly_dataframe = pd.DataFrame(data=hourly_data)
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_datetime_dataframe = pd.DataFrame({"datetime": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )})
    vfunc = np.vectorize(weather_code_to_description)
    daily_data = {
        "date": pd.to_datetime(daily_datetime_dataframe["datetime"]).dt.date,
        "description": vfunc(daily_weather_code)
    }
    daily_dataframe = pd.DataFrame(data=daily_data)
    return daily_dataframe, hourly_dataframe


def weather_code_to_description(code):
    try:
        description = wmo_codes[code]
    except KeyError:
        scheduler.app.logger.debug(f"Weather code '{code}' is unknown")
        description = "Unknown"
    return description


def get_sunrise(sun, tz, date, min_time):
    dt = datetime.combine(date, min_time)
    sunrise = sun.get_sunrise_time(dt, tz).time()
    return sunrise


def get_sunset(sun, tz, date, min_time):
    dt = datetime.combine(date, min_time)
    sunset = sun.get_sunset_time(dt, tz).time()
    return sunset


def add_sun(daily_dataframe):
    min_time = datetime.min.time()
    tz = pytz.timezone(scheduler.app.config["TIMEZONE"])
    sun = Sun(scheduler.app.config["LATITUDE"], scheduler.app.config["LONGITUDE"])
    dates = daily_dataframe["date"].to_list()
    

def insert_into_db(daily_dataframe, hourly_dataframe):
    """TODO"""
    
    pass


wmo_codes = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Freezing Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Slight or Moderate Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}


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
