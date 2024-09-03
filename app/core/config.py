"""Configuration settings used by flask application."""
import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config(object):
    SECRET_KEY = os.urandom(12).hex()
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "core", "default.db")
    SQLALCHEMY_BINDS = {
        "users": "sqlite:///" + os.path.join(basedir, "auth", "users.db"),
        "weather": "sqlite:///" + os.path.join(basedir, "weather", "weather.db"),
        "water": "sqlite:///" + os.path.join(basedir, "water", "water.db")
    }
    SCHEDULER_API_ENABLED = True
    URL = "https://api.open-meteo.com/v1/forecast"
    CITY = "Cardiff"
    REGION = "Wales"
    LATITUDE = 51.48
    LONGITUDE = -3.18
    TIMEZONE = "Europe/London"
