from app import db
from app.auth.models import User
from werkzeug.security import generate_password_hash


def init_accounts():
    users = User.query.all()
    if not users:
        username = "admin"
        password = generate_password_hash("admin")
        default_account = User(username=username, password=password)
        db.session.add(default_account)
        db.session.commit()
