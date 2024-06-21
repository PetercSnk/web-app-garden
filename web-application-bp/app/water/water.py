from flask import render_template, flash, current_app
from flask_login import login_required, current_user
from app.water.models import Water, WaterStatus
from app import db
from app.core.extensions import event
import threading
#from app.water.systems import valve_obj, pump_obj
from datetime import datetime
import time
from app.water import water_bp
from app.water.forms import WaterForm, CancelForm


@water_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    water_status = WaterStatus.query.first()
    water_form = WaterForm()
    cancel_form = CancelForm()
    if water_form.water_submit.data and water_form.validate():
        if water_status.status:
            flash("Already Runnning", category="error")
        else:
            water_time = water_form.water_time.data
            # REPLACE None with valve_obj and pump_obj
            thread = threading.Thread(target=water, args=(current_app._get_current_object(), water_time, None, None), daemon=True)
            thread.start()
            flash("Started Process", category="success")
            return render_template("water/water.html", user=current_user, status=True, water_form=water_form, cancel_form=cancel_form)
    elif cancel_form.cancel_submit.data and cancel_form.validate():
        if water_status.status:
            event.set()
            flash("Stopped Process", category="success")
            return render_template("water/water.html", user=current_user, status=False, water_form=water_form, cancel_form=cancel_form)
        else:
            flash("Not Running", category="error")
    return render_template("water/water.html", user=current_user, status=water_status.status, water_form=water_form, cancel_form=cancel_form)


def water(app, water_time, valve_obj, pump_obj):
    with app.app_context():
        water_status = WaterStatus.query.first()
        water_status.status = True
        db.session.add(Water(start_date_time=datetime.now(), duration=water_time))
        db.session.commit()
        app.logger.info(f"Watering for {water_time} seconds")
        # valve.valve_on()
        # pump.pump_on()
        loop(app, water_time)
        # valve.valve_off()
        # pump.pump_off()
        app.logger.info("Finished watering process")
        water_status.status = False
        db.session.commit()
    return


def loop(app, water_time):
    for x in range(water_time):
        time.sleep(1)
        if event.is_set():
            app.logger.debug("Event set")
            event.clear()
            return
