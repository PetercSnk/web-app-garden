from app import db


class Water(db.Model):
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    start_date_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)

    def __repr__(self):
        return f"<Water: {self.start_date_time}>"


class WaterStatus(db.Model):
    __bind_key__ = "water"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean)

    def __repr__(self):
        return f"<WaterStatus: {self.status}>"
