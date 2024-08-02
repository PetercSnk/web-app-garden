"""All tables used by the auth module."""
from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    """Model for user table."""
    __bind_key__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(256))

    def __repr__(self):
        return f"<User: {self.username}>"
