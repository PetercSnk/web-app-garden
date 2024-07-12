import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config(object):
    SECRET_KEY = os.urandom(12).hex()
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "core", "instance", "default.db")
    SQLALCHEMY_BINDS = {
        "users": "sqlite:///" + os.path.join(basedir, "auth", "instance", "users.db"),
        "weather": "sqlite:///" + os.path.join(basedir, "weather", "instance", "weather.db"),
        "water": "sqlite:///" + os.path.join(basedir, "water", "instance", "water.db")
    }
    SCHEDULER_API_ENABLED = True
    BASE_URL = "http://api.openweathermap.org/data/2.5/forecast?"
    API_KEY = "7003cd97625df5e3aba0aa06cc93f3ad"
    LATITUDE = 51.529
    LONGITUDE = -3.191
    TIMEZONE = "Europe/London"
