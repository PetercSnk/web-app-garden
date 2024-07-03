from app.water.models import Plant, System
from app.water import systems
from app import db
import sys
import inspect


def get_classes(package):
    # get all classes in package
    classes = []
    for name, _class in inspect.getmembers(sys.modules[package]):
        if inspect.isclass(_class):
            classes.append((name, _class))
    return classes


def setup_plants():
    # create default plant if none exist otherwise set all statuses to false
    plants = Plant.query.all()
    if not plants:
        db.session.add(Plant(name="Default", description="Default", status=False))
    else:
        for plant in plants:
            plant.status = False
    db.session.commit()


def setup_systems():
    # add all systems to system table
    existing_systems = [system.name for system in System.query.all()]
    classes = get_classes(systems)
    for name, _class in classes:
        if name not in existing_systems:
            obj = _class()
            db.session.add(System(name=name, obj=obj))
    db.session.commit()
