from flask import render_template, flash, current_app
from flask_login import login_required, current_user
from app.core.extensions import event
from app.water.models import Water, WaterStatus
from app.water.forms import WaterForm, CancelForm, AutoForm
from app.water import water_bp
from app import db
import threading
#from app.water.systems import valve_obj, pump_obj
from datetime import datetime
import time


@water_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    water_status = WaterStatus.query.first()
    water_form = WaterForm()
    cancel_form = CancelForm()
    auto_form = AutoForm()
    if water_form.submit.data and water_form.validate():
        if water_status.status:
            flash("Already Runnning", category="error")
        else:
            duration_sec = water_form.duration_sec.data
            # REPLACE None with valve_obj and pump_obj
            thread = threading.Thread(target=water, args=(current_app._get_current_object(), duration_sec, None, None), daemon=True)
            thread.start()
            current_app.logger.debug("Started thread")
            flash("Started Process", category="success")
            return render_template("water/water.html", user=current_user, status=True, water_form=water_form, cancel_form=cancel_form, auto_form=auto_form)
    elif cancel_form.submit.data and cancel_form.validate():
        if water_status.status:
            event.set()
            current_app.logger.debug("Event set")
            flash("Stopped Process", category="success")
            return render_template("water/water.html", user=current_user, status=False, water_form=water_form, cancel_form=cancel_form, auto_form=auto_form)
        else:
            flash("Not Running", category="error")
    elif auto_form.submit.data and auto_form.validate():
        pass
    return render_template("water/water.html", user=current_user, status=water_status.status, water_form=water_form, cancel_form=cancel_form, auto_form=auto_form)


def water(app, duration_sec, valve_obj, pump_obj):
    with app.app_context():
        water_status = WaterStatus.query.first()
        water_status.status = True
        db.session.add(Water(start_date_time=datetime.now(), duration_sec=duration_sec))
        db.session.commit()
        app.logger.debug(f"Water status set to {water_status.status}")
        app.logger.info(f"Watering for {duration_sec} seconds")
        # valve.valve_on()
        # pump.pump_on()
        loop(app, duration_sec)
        # valve.valve_off()
        # pump.pump_off()
        app.logger.info("Finished watering process")
        water_status.status = False
        db.session.commit()
        app.logger.debug(f"Water status set to {water_status.status}")
    return


def loop(app, duration_sec):
    for x in range(duration_sec):
        time.sleep(1)
        if event.is_set():
            app.logger.debug("Loop stopped")
            event.clear()
            return
