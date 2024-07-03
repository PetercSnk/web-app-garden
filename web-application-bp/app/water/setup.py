from app.water.models import Plant, System
from app.water import systems
from app import db
import inspect


def get_classes(package):
    """Get all classes in package"""
    classes = []
    for name, _class in inspect.getmembers(package):
        if inspect.isclass(_class):
            classes.append((name, _class))
    return classes


def init_systems():
    """Reset & load available systems into database"""
    existing_systems = [system.name for system in System.query.all()]
    classes = get_classes(systems)
    for name, _class in classes:
        obj = _class()
        obj.off()
        if name not in existing_systems:
            db.session.add(System(name=name, obj=obj))
    db.session.commit()
    return


def reset_statuses():
    """Reset all statuses"""
    plants = Plant.query.all()
    if plants:
        for plant in plants:
            plant.status = False
        db.session.commit()
    return
