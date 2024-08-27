"""All tables used by the water module."""
from app import db


class System(db.Model):
    """Model for system table."""
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    obj = db.Column(db.PickleType)
    plant = db.relationship("Plant", uselist=False, backref="system")

    def __repr__(self):
        return f"<System: {self.name}>"


class Plant(db.Model):
    """Model for plant table."""
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey("system.id"))
    name = db.Column(db.String)
    description = db.Column(db.String)
    status = db.Column(db.Boolean)
    history = db.relationship("History", backref="plant", cascade="all, delete-orphan")
    config = db.relationship("Config", uselist=False, backref="plant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plant: {self.name}>"


class History(db.Model):
    """Model for history table."""
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"))
    start_date_time = db.Column(db.DateTime)
    duration_sec = db.Column(db.Integer)

    def __repr__(self):
        return f"<History: {self.start_date_time}>"


class Config(db.Model):
    """Model for config table."""
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"))
    enabled = db.Column(db.Boolean)
    duration_sec = db.Column(db.Integer)
    occurrence_days = db.Column(db.Integer)
    mode = db.Column(db.Integer)
    default = db.Column(db.Time)
    rain_reset = db.Column(db.Boolean)
    threshold_mm = db.Column(db.Integer)
    last_edit = db.Column(db.DateTime)
    job_init = db.Column(db.DateTime)
    job_due = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Config: {self.id}>"
