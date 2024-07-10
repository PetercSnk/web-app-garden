from app.water.models import Plant, System
from app.water import systems
from app import db, events
from threading import Event
import inspect


def get_classes(package):
    """Get all classes in package."""
    classes = []
    for name, _class in inspect.getmembers(package):
        if inspect.isclass(_class):
            classes.append((name, _class))
    return classes


def init_systems():
    """
    Reset & load available systems into database.

    Run this function on startup.
    """
    existing_systems = [system.name for system in System.query.all()]
    classes = get_classes(systems)
    for name, _class in classes:
        obj = _class()
        obj.off()
        if name not in existing_systems:
            db.session.add(System(name=name, obj=obj))
    db.session.commit()
    return


def init_plants():
    """
    Reset statuses & create event obj for each plant.

    Run this function on startup.
    """
    plants = Plant.query.all()
    if plants:
        for plant in plants:
            events[plant.name] = Event()
            plant.status = False
        db.session.commit()
    return
