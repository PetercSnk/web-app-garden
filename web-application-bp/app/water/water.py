from flask import render_template, request, flash
from flask_login import login_required, current_user
from app.water.models import Water, WaterStatus
from app import db
from app.core.extensions import event, executor
from datetime import datetime
import time
# from .pump import Pump
# from .valve import Valve
from app.water import water_bp


@water_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    water_status = WaterStatus.query.first()
    if request.method == "POST":
        if "wtime" in request.form:
            if water_status.status:
                flash("Already Runnning", category="error")
            else:
                water_time = int(request.form.get("wtime"))
                water_status.status = True
                db.session.add(Water(start_date_time=datetime.now(), duration=water_time))
                db.session.commit()
                water.submit(water_time)
                flash("Started Process", category="success")
        elif "fstop" in request.form:
            if water_status.status:
                event.set()
                water_status.status = False
                db.session.commit()
                flash("Stopped Process", category="error")
            else:
                flash("Not Running", category="error")
    return render_template("water/water.html", user=current_user, status=water_status.status)


@executor.job
def water(water_time):
    # valve = Valve()
    # pump = Pump()
    # valve.valve_on()
    # pump.pump_on()
    for x in range(water_time):
        time.sleep(1)
        if event.is_set():
            # valve.valve_off()
            # pump.pump_off()
            event.clear()
            return
    # valve.valve_off()
    # pump.pump_off()
    water_status = WaterStatus.query.first()
    water_status.status = False
    db.session.commit()
    return
