from app.water.models import WaterStatus
from app import db


def restart(app):
    with app.app_context():
        water_status = WaterStatus.query.first()
        if not water_status:
            db.session.add(WaterStatus(status=False))
        else:
            water_status.status = False
        db.session.commit()

        # from app.water.systems import valve_obj, pump_obj
        # valve_obj.valve_off()
        # pump_obj.pump_off()
