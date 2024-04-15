from flask import render_template, Blueprint, request, flash, redirect
from flask_login import login_required, current_user
from threading import Event
from .models import Weather, Day, Water, WaterStatus, db
from datetime import datetime
from . import jobs
# from .pump import Pump
# from .valve import Valve
import time
from . import executor

routes = Blueprint("routes", __name__)
event = Event()

@routes.route("/", methods=["GET", "POST"])
@login_required
def home():
    db_days = Day.query.order_by(Day.date).all()
    date = sunrise = sunset = time_weather_labels = time = temperature = humidity = weather = rain_chance = rain_recorded = 0
    if request.method == "POST":
        # can this be made GET? date as arg and in url
        if "get-day" in request.form:
            date = request.form["get-day"]
            sunrise, sunset, time_weather_labels, temperature, humidity, rain_chance, rain_recorded = format_for_graph(date)
        elif "get-weather" in request.form:
            msg = jobs.get_weather()
            flash(msg, category="info")
            return redirect("/")
        else:
            return redirect("/")
    else:
        if db_days:
            date = Day.query.order_by(Day.date).first().date
            sunrise, sunset, time_weather_labels, temperature, humidity, rain_chance, rain_recorded = format_for_graph(date)     
    return render_template("home.html", user=current_user, db_days=db_days, date=date, sunrise=sunrise, sunset=sunset, time_weather_labels=time_weather_labels, temperature=temperature, humidity=humidity, rain_chance=rain_chance, rain_recorded=rain_recorded)

@routes.route("/water", methods=["GET", "POST"])
@login_required
def water():
    water_status = WaterStatus.query.first()
    if request.method == "POST":
        water_status = WaterStatus.query.first()
        if "wtime" in request.form:
            if water_status.status:
                flash("Already Runnning", category="error")          
            else:
                water_time = int(request.form.get("wtime"))
                water_status.status = True
                db.session.add(Water(start_date_time=datetime.now(), duration=water_time))
                db.session.commit()
                executor.submit(water_event, water_time)
        elif "fstop" in request.form:
            if water_status.status:
                event.set()
                water_status.status = False
                db.session.commit()
            else:
                flash("Not Running", category="error")
    return render_template("water.html", user=current_user, status=water_status.status)

def water_event(water_time):
    # water_status = WaterStatus.query.first()
    # pump_relay = 16
    # valve_relay = 18
    # valve_switch = 12
    # valve = Valve(valve_relay, valve_switch)
    # pump = Pump(pump_relay)
    # valve.valve_on()
    # pump.pump_on()
    # for x in range(water_time):
    #     time.sleep(1)
    #     if event.is_set():
    #         valve.valve_off()
    #         pump.pump_off()
    #         event.clear()
    #         return
    # valve.valve_off()
    # pump.pump_off()
    # water_status.status = False
    # db.session.commit()
    return

def format_for_graph(date):
    day = Day.query.filter(Day.date==date).first()
    weather = Weather.query.filter(Weather.day_id==day.id).order_by(Weather.time).all()
    sunrise = day.sunrise
    sunset = day.sunset
    labels, temperature_c, humidity, rain_probability, rain_volume_mm = [], [], [], [], []
    for three_hour_step in weather:
        labels.append(f"{three_hour_step.time.strftime('%H:%M:%S')} {three_hour_step.description.title()}")
        temperature_c.append(three_hour_step.temperature_c)
        humidity.append(three_hour_step.humidity)
        rain_probability.append(three_hour_step.rain_probability)
        rain_volume_mm.append(three_hour_step.rain_volume_mm)
    return sunrise, sunset, labels, temperature_c, humidity, rain_probability, rain_volume_mm