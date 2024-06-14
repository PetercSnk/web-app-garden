from app import db


class Day(db.Model):
    __bind_key__ = "weather"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    sunrise = db.Column(db.Time)
    sunset = db.Column(db.Time)
    weather = db.relationship("Weather", backref="day", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Day: {self.date}>"


class Weather(db.Model):
    __bind_key__ = "weather"
    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey("day.id"))
    time = db.Column(db.Time)
    temperature_c = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    description = db.Column(db.String(64))
    rain_probability = db.Column(db.Integer)
    rain_volume_mm = db.Column(db.Integer)

    def __repr__(self):
        return f"<Weather: {self.day_id}>"
