from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from threading import Event
from .models import Weather, Day, Water, WaterStatus, db
from datetime import datetime
from . import jobs
import time
from . import executor
# from .pump import Pump
# from .valve import Valve

routes = Blueprint("routes", __name__)
event = Event()

@routes.route("/", methods=["GET"])
@login_required
def home():
    today = datetime.now().date()
    db_today = Day.query.filter(Day.date==today).one()
    if db_today:
        # redirect to todays id if it exists in db
        return redirect(url_for("routes.weather", day_id=db_today.id))
    else:
        db_first = Day.query.first()
        if db_first:
            # redirect to some other id that exists if today is not in db
            return redirect(url_for("routes.weather", day_id=db_first.id))
        else:
            # if nothing exists in db redirect to /0
            return redirect(url_for("routes.weather", day_id=0))

@routes.route("/weather/<int:day_id>", methods=["GET", "POST"])
@login_required
def weather(day_id):
    if request.method == "POST":
        if "get-weather" in request.form:
            msg = jobs.get_weather()
            flash(msg, category="info")
            return redirect(url_for("routes.weather", day_id=day_id))
    else:
        db_days = Day.query.order_by(Day.date).all()
        if day_id > 0:
            date, sunrise, sunset, labels, temperature_c, humidity, rain_probability, rain_volume_mm = format_for_graph(day_id)
            return render_template("weather.html", user=current_user, db_days=db_days, date=date, sunrise=sunrise, sunset=sunset, labels=labels, temperature_c=temperature_c, humidity=humidity, rain_probability=rain_probability, rain_volume_mm=rain_volume_mm)
        else:
            return render_template("weather.html", user=current_user, db_days=db_days, date=None, sunrise=None, sunset=None, labels=0, temperature_c=0, humidity=0, rain_probability=0, rain_volume_mm=0)

@routes.route("/water", methods=["GET", "POST"])
@login_required
def water():
    water_status = WaterStatus.query.one()
    if request.method == "POST":
        if "wtime" in request.form:
            if water_status.status:
                flash("Already Runnning", category="error")          
            else:
                water_time = int(request.form.get("wtime"))
                water_status.status = True
                db.session.add(Water(start_date_time=datetime.now(), duration=water_time))
                db.session.commit()
                executor.submit(water_event, water_time)
                flash("Started Process", category="success")   
        elif "fstop" in request.form:
            if water_status.status:
                event.set()
                water_status.status = False
                db.session.commit()
                flash("Stopped Process", category="error") 
            else:
                flash("Not Running", category="error")
    return render_template("water.html", user=current_user, status=water_status.status)

def format_for_graph(day_id):
    day = Day.query.filter(Day.id==day_id).one()
    weather = Weather.query.filter(Weather.day_id==day.id).order_by(Weather.time).all()
    labels, temperature_c, humidity, rain_probability, rain_volume_mm = [], [], [], [], []
    for three_hour_step in weather:
        labels.append(f"{three_hour_step.time.strftime('%H:%M')} {three_hour_step.description.title()}")
        temperature_c.append(three_hour_step.temperature_c)
        humidity.append(three_hour_step.humidity)
        rain_probability.append(three_hour_step.rain_probability)
        rain_volume_mm.append(three_hour_step.rain_volume_mm)
    return day.date, day.sunrise, day.sunset, labels, temperature_c, humidity, rain_probability, rain_volume_mm

@routes.context_processor
def utility():
    def format_date(datetime_obj):
        return datetime_obj.strftime("%d-%b")
    return dict(format_date=format_date)

def water_event(water_time):
    water_status = WaterStatus.query.one()
    # pump_relay = 16
    # valve_relay = 18
    # valve_switch = 12
    # valve = Valve(valve_relay, valve_switch)
    # pump = Pump(pump_relay)
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
    water_status.status = False
    db.session.commit()
    return
