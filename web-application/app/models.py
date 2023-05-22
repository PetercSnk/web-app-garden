from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(256))

class ThreeHour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    temperature = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    weather = db.Column(db.String(64))
    rain_chance = db.Column(db.Integer)
    rain_recorded = db.Column(db.Integer)

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    sunrise = db.Column(db.Time)
    sunset = db.Column(db.Time)