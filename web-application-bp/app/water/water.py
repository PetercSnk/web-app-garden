from flask import render_template, flash, current_app
from flask_login import login_required, current_user
from app.core.extensions import event
from app.water.models import Water, WaterStatus, WaterConfig
from app.water.forms import WaterForm, CancelForm, ConfigForm
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
    config = WaterConfig.query.first()
    forms = {
        "water": WaterForm(),
        "cancel": CancelForm(),
        "config": ConfigForm()
    }
    if forms["water"].submit.data and forms["water"].validate():
        if water_status.status:
            flash("Already Runnning", category="error")
        else:
            duration_sec = forms["water"].duration_sec.data
            # REPLACE None with valve_obj and pump_obj
            thread = threading.Thread(target=water, args=(current_app._get_current_object(), duration_sec, None, None), daemon=True)
            thread.start()
            current_app.logger.debug("Started thread")
            flash("Started Process", category="success")
            return render_template("water/water.html",
                                   user=current_user,
                                   status=True,
                                   forms=forms)
    elif forms["cancel"].submit.data and forms["cancel"].validate():
        if water_status.status:
            event.set()
            current_app.logger.debug("Event set")
            flash("Stopped Process", category="success")
            return render_template("water/water.html",
                                   user=current_user,
                                   status=False,
                                   forms=forms)
        else:
            flash("Not Running", category="error")
    elif forms["config"].submit.data and forms["config"].validate():
        if config:
            config.enabled = forms["config"].enabled.data
            config.duration_sec = forms["config"].duration_sec.data
            config.min_wait_hr = forms["config"].win_wait_hr.data
            config.mode = forms["config"].mode.data
            config.default = forms["config"].default.data
            config.rain_reset = forms["config"].rain_reset.data
        else:
            new_config = WaterConfig(enabled=forms["config"].enabled.data,
                                     duration_sec=forms["config"].duration_sec.data,
                                     min_wait_hr=forms["config"].min_wait_hr.data,
                                     mode=forms["config"].mode.data,
                                     default=forms["config"].default.data,
                                     rain_reset=forms["config"].rain_reset.data)
            db.session.add(new_config)
        db.session.commit()
    config = WaterConfig.query.first()
    return render_template("water/water.html",
                           user=current_user,
                           status=water_status.status,
                           config=config,
                           forms=forms)


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
