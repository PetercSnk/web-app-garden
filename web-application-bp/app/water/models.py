from app import db


class Selected(db.Model):
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    plant = db.relationship("Plant", backref="selected")


class Plant(db.Model):
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    selected_id = db.Column(db.Integer, db.ForeignKey("selected.id"))
    name = db.Column(db.String)
    description = db.Column(db.String)
    status = db.Column(db.Boolean)
    history = db.relationship("History", backref="plant", cascade="all, delete-orphan")
    config = db.relationship("Config", backref="plant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plant: {self.name}>"


class History(db.Model):
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"))
    start_date_time = db.Column(db.DateTime)
    duration_sec = db.Column(db.Integer)

    def __repr__(self):
        return f"<Water: {self.start_date_time}>"


class Config(db.Model):
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"))
    enabled = db.Column(db.Boolean)
    duration_sec = db.Column(db.Integer)
    min_wait_hr = db.Column(db.Integer)
    mode = db.Column(db.Integer)
    default = db.Column(db.Time)
    rain_reset = db.Column(db.Boolean)
    estimate = db.Column(db.DateTime)

    def __repr__(self):
        return f"<WaterAuto: {self.id}"
