from flask_executor import Executor
from flask_apscheduler import APScheduler
from threading import Event


executor = Executor()
scheduler = APScheduler()
event = Event()
