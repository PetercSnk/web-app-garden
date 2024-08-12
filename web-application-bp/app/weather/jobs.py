"""All functions required for scheduling the retrieval of weather data."""
from datetime import datetime
import os
import yaml
import requests
import traceback
import pytz
import openmeteo_requests
import pandas as pd
import numpy as np
from suntime import Sun
from astral import LocationInfo
from astral.sun import sun
from app.weather.models import Daily, Hourly
from app import db, scheduler


@scheduler.task("cron", id="get_weather", minute="0", hour="1", day="*", month="*", day_of_week="*")
def get_weather():
    response = get_response()
    daily_dataframe, hourly_dataframe = format_response(response)
    daily_dataframe = insert_descriptions(daily_dataframe)
    daily_dataframe = insert_suntimes(daily_dataframe)
    insert_into_db(daily_dataframe, hourly_dataframe)
    # print(daily_dataframe)
    # print(hourly_dataframe)


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
    daily_data = {
        "date": pd.to_datetime(daily_datetime_dataframe["datetime"]).dt.date,
        "weather_code": daily_weather_code
    }
    daily_dataframe = pd.DataFrame(data=daily_data)
    return daily_dataframe, hourly_dataframe


def get_description(wmo_codes, code):
    try:
        description = wmo_codes["codes"][code]
    except KeyError:
        scheduler.app.logger.debug(f"Weather code '{code}' is unknown")
        description = "Unknown"
    return description


def insert_descriptions(daily_dataframe):
    vfunc = np.vectorize(get_description)
    base_path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(base_path, "wmo_codes.yaml")
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    daily_dataframe["weather_description"] = vfunc(data, daily_dataframe["weather_code"])
    return daily_dataframe


def get_suntimes(city, tz, date):
    s = sun(city.observer, tzinfo=tz, date=date)
    sunrise = s["sunrise"].time().replace(microsecond=0)
    sunset = s["sunset"].time().replace(microsecond=0)
    return sunrise, sunset


def insert_suntimes(daily_dataframe):
    """can use apply here?? and on insert"""
    city = LocationInfo(scheduler.app.config["CITY"],
                        scheduler.app.config["REGION"],
                        scheduler.app.config["TIMEZONE"],
                        scheduler.app.config["LATITUDE"],
                        scheduler.app.config["LONGITUDE"])
    tz = pytz.timezone(scheduler.app.config["TIMEZONE"])
    vfunc = np.vectorize(get_suntimes)
    daily_dataframe["sunrise"], daily_dataframe["sunset"] = vfunc(city, tz, daily_dataframe["date"])
    return daily_dataframe


def add_daily_to_db(row, existing_dates):
    with scheduler.app.app_context():
        if row["date"] not in existing_dates:
            daily = Daily(date=row["date"],
                          sunrise=row["sunrise"],
                          sunset=row["sunset"],
                          weather_code=row["weather_code"],
                          weather_description=row["weather_description"])
            db.session.add(daily)
            db.session.commit()
            return row["date"]


def insert_into_db(daily_dataframe, hourly_dataframe):
    existing_dates = [day.date for day in Daily.query.all()]
    dates_added = daily_dataframe.apply(add_daily_to_db, existing_dates=existing_dates, axis=1)
    print(dates_added)
    # for index, row in daily_dataframe.iterrows():
    #     print(row)
    #     h = hourly_dataframe.loc[hourly_dataframe["date"] == row["date"]]
    #     print(h)
    pass


# def kelvin_to_celsius(kelvin):
#     return (kelvin - 273.15)
#
#
# def request_weather():
#     try:
#         config = scheduler.app.config
#         url = f"{config['BASE_URL']}lat={config['LATITUDE']}&lon={config['LONGITUDE']}&appid={config['API_KEY']}"
#         request = requests.get(url)
#         scheduler.app.logger.debug(f"Request made to {url}")
#         json = request.json()
#         request.raise_for_status()
#     except Exception as error:
#         scheduler.app.logger.error(f"A {type(error).__name__} has occured | {request.status_code} {request.reason} | Response {json}")
#     return request.ok, json
#
#
# def extract_data(json):
#     try:
#         organised_forecast = {}
#         timezone = pytz.timezone(scheduler.app.config["TIMEZONE"])
#         five_day_forecast = json["list"]
#         for three_hour_step in five_day_forecast:
#             date_time = datetime.utcfromtimestamp(three_hour_step["dt"])
#             weather_data = {
#                 "time": date_time.time(),
#                 "temperature_c": round(kelvin_to_celsius(three_hour_step["main"]["temp"]), 2),
#                 "humidity": three_hour_step["main"]["humidity"],
#                 "description": three_hour_step["weather"][0]["description"],
#                 "rain_probability": three_hour_step["pop"]
#             }
#             # the volume of rain fall is not always included, check it exists or set it to zero
#             if "rain" in three_hour_step:
#                 weather_data["rain_volume_mm"] = three_hour_step["rain"]["3h"]
#             else:
#                 weather_data["rain_volume_mm"] = 0
#             # store all three houlry weather data, sunrise, and sunset for its date in organised forecast
#             date = date_time.date()
#             if date in organised_forecast:
#                 organised_forecast[date]["weather_data"].append(weather_data)
#             else:
#                 sun = Sun(scheduler.app.config["LATITUDE"], scheduler.app.config["LONGITUDE"])
#                 organised_forecast[date] = {"weather_data": [weather_data], "sunrise": sun.get_sunrise_time(date_time, timezone).time(), "sunset": sun.get_sunset_time(date_time, timezone).time()}
#         return organised_forecast
#     except Exception as error:
#         scheduler.app.logger.error(f"A {type(error).__name__} has occured | {traceback.format_exc()}")
#         return {}
#
#
# def remove_missing(organised_forecast):
#     # remove entries that have missing data, for some reason openweathermap include a 6th day in a 5 day forecast which has missing data
#     remove = []
#     remove_log = []
#     for date, data in organised_forecast.items():
#         if len(data["weather_data"]) < 8:
#             remove.append(date)
#             remove_log.append(date.strftime("%d/%m/%y"))
#     for date in remove:
#         organised_forecast.pop(date)
#     scheduler.app.logger.debug(f"Dates {remove_log} contain missing data, removing")
#     return organised_forecast
#
#
# def add_to_db(organised_forecast):
#     with scheduler.app.app_context():
#         dates = [day.date for day in Day.query.order_by(Day.date).all()]
#         add_log = []
#         exists_log = []
#         for date, data in organised_forecast.items():
#             if date not in dates:
#                 day = Day(date=date, sunrise=data["sunrise"], sunset=data["sunset"])
#                 add_log.append(date.strftime("%d/%m/%y"))
#                 for weather_data in data["weather_data"]:
#                     weather = Weather(time=weather_data["time"], temperature_c=weather_data["temperature_c"], humidity=weather_data["humidity"], description=weather_data["description"], rain_probability=weather_data["rain_probability"], rain_volume_mm=weather_data["rain_volume_mm"])
#                     day.weather.append(weather)
#                 db.session.add(day)
#             else:
#                 exists_log.append(date.strftime("%d/%m/%y"))
#         db.session.commit()
#     scheduler.app.logger.debug(f"Dates {exists_log} already exist in database")
#     scheduler.app.logger.debug(f"Dates {add_log} added to database")
#     return add_log
#
#
# @scheduler.task("cron", id="delete_old_records", minute="30", hour="1", day="*", month="*", day_of_week="*")
# def delete_old_records():
#     with scheduler.app.app_context():
#         days = Day.query.order_by(Day.date).all()
#         # keeps data for only 7 days
#         delete = days[:-7]
#         delete_log = []
#         if delete:
#             for day in delete:
#                 delete_log.append(day.date.strftime("%d/%m/%y"))
#                 db.session.delete(day)
#             db.session.commit()
#     scheduler.app.logger.debug(f"Deleted {delete_log} from database")
#     return
