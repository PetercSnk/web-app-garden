from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(256))

class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey("day.id"))
    time = db.Column(db.Time)
    temperature_c = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    description = db.Column(db.String(64))
    rain_probability = db.Column(db.Integer)
    rain_volume_mm = db.Column(db.Integer)

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    sunrise = db.Column(db.Time)
    sunset = db.Column(db.Time)
    weather = db.relationship("Weather", backref="day")

class Water(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)

class WaterStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean)