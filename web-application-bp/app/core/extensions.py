from flask_apscheduler import APScheduler
from threading import Event


scheduler = APScheduler()
event = Event()
