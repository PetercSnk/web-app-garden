from . import create_app, db
import datetime
import requests
from threading import Thread

app = create_app()

if __name == "__main__":
    app.run