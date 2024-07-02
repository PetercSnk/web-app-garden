from app.water.models import Plant, System
from app.water import systems
from app import db
import sys
import inspect


objs = []
for name, obj in inspect.getmembers(sys.modules[systems]):
    if inspect.isclass(obj):
        objs.append((name, obj))


def setup():
    # create default plant if none exist otherwise set its status to false
    plants = Plant.query.all()
    if not plants:
        db.session.add(Plant(name="Default", description="Default", status=False))
    else:
        for plant in plants:
            plant.status = False
    system_names = [system.name for system in System.query.all()]
    for obj in objs:
        if obj[0] not in system_names:
            db.session.add(System(name=obj[0], obj=obj[1]))
    db.session.commit()
