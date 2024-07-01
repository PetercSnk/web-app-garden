from app.water.models import Plant
from app import db


def plants_setup():
    plants = Plant.query.all()
    if not plants:
        db.session.add(Plant(name="Default", description="Default", status=False))
    else:
        for plant in plants:
            plant.status = False
    db.session.commit()


def systems_setup(objs):
    for obj in objs:
        obj.off()
