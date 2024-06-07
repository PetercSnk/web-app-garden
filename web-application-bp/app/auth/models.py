from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    __bind_key__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(256))

    def __repr__(self):
        return f"<User: {self.username}>"
