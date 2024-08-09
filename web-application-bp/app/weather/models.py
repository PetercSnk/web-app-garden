from app import db


class Daily(db.Model):
    __bind_key__ = "weather"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    sunrise = db.Column(db.Time)
    sunset = db.Column(db.Time)
    weather_code = db.Column(db.Integer)
    weather_description = db.Column(db.String(64))
    hourly = db.relationship("Hourly", backref="day", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Day: {self.date}>"


class Hourly(db.Model):
    __bind_key__ = "weather"
    id = db.Column(db.Integer, primary_key=True)
    daily_id = db.Column(db.Integer, db.ForeignKey("daily.id"))
    time = db.Column(db.Time)
    temperature = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    precipitation_probability = db.Column(db.Integer)
    precipitation = db.Column(db.Integer)

    def __repr__(self):
        return f"<Weather: {self.day_id}>"
