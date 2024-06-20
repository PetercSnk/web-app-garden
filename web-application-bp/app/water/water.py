from flask import render_template, request, flash, current_app, url_for, redirect
from flask_login import login_required, current_user
from app.water.models import Water, WaterStatus
from app import db
from app.core.extensions import event
import threading
#from app.water.systems import valve_obj, pump_obj
from datetime import datetime
import time
from app.water import water_bp


@water_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    water_status = WaterStatus.query.first()
    if request.method == "POST":
        if "water" in request.form:
            if water_status.status:
                flash("Already Runnning", category="error")
            else:
                water_time = int(request.form.get("water"))
                # REPLACE None with valve_obj and pump_obj
                thread = threading.Thread(target=water, args=(current_app._get_current_object(), water_time, None, None), daemon=True)
                thread.start()
                flash("Started Process", category="success")
                return render_template("water/water.html", user=current_user, status=True)
        elif "stop" in request.form:
            if water_status.status:
                event.set()
                flash("Stopped Process", category="success")
                return render_template("water/water.html", user=current_user, status=False)
            else:
                flash("Not Running", category="error")
    return render_template("water/water.html", user=current_user, status=water_status.status)


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
