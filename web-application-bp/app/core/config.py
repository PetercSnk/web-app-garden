class Config(object):
    SECRET_KEY = "GardenPi"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    EXECUTOR_TYPE = "thread"
    SCHEDULER_API_ENABLED = True