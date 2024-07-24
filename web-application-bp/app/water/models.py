from app import db


class System(db.Model):
    """Connected systems/devices."""
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    obj = db.Column(db.PickleType)
    plant = db.relationship("Plant", uselist=False, backref="system")

    def __repr__(self):
        return f"<System: {self.name}>"


class Plant(db.Model):
    """Information about plants."""
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey("system.id"))
    name = db.Column(db.String)
    description = db.Column(db.String)
    status = db.Column(db.Boolean)
    estimate = db.Column(db.DateTime)
    history = db.relationship("History", backref="plant", cascade="all, delete-orphan")
    config = db.relationship("Config", uselist=False, backref="plant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plant: {self.name}>"


class History(db.Model):
    """Watering history for plants."""
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"))
    start_date_time = db.Column(db.DateTime)
    duration_sec = db.Column(db.Integer)

    def __repr__(self):
        return f"<History: {self.start_date_time}>"


class Config(db.Model):
    """Automated watering configuration for plants."""
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"))
    enabled = db.Column(db.Boolean)
    duration_sec = db.Column(db.Integer)
    occurrence_days = db.Column(db.Integer)
    mode = db.Column(db.Integer)
    default = db.Column(db.Time)
    rain_reset = db.Column(db.Boolean)

    def __repr__(self):
        return f"<Config: {self.id}>"
