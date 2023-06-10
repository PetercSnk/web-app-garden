from flask import render_template, Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from threading import Thread
from . import db
from .models import ThreeHour, Day
import requests
from datetime import datetime
from sqlalchemy import desc
from .pump import Pump
from .valve import Valve

routes = Blueprint("routes", __name__)

@routes.route("/home", methods=["GET", "POST"])
@login_required
def home():
    all_day = Day.query.order_by(Day.date).all()
    if all_day:
        if request.method == "POST":
            if "get-day" in request.form:
                date = request.form["get-day"]
                sunrise, sunset, time_weather_labels, temperature, humidity, rain_chance, rain_recorded = format_for_graph(date)
        else:
            date = Day.query.order_by(Day.date).first().date
            sunrise, sunset, time_weather_labels, temperature, humidity, rain_chance, rain_recorded = format_for_graph(date)
    else:
        date = sunrise = sunset = time = temperature = humidity = weather = rain_chance = rain_recorded = 0
    return render_template("home.html", user=current_user, all_day=all_day, date=date, sunrise=sunrise, sunset=sunset, time_weather_labels=time_weather_labels, temperature=temperature, humidity=humidity, rain_chance=rain_chance, rain_recorded=rain_recorded)

@routes.route("/water", methods=["GET", "POST"])
@login_required
def water():
    if request.method == "POST":
        water_time = request.form.get("wtime")
        # script to water
        thread = Thread(target=run_water(water_time), daemon=True, name="water")
    return render_template("water.html", user=current_user)

def run_water(water_time):
    pump_relay = 16
    valve_relay = 18
    valve_switch = 12
    valve = Valve(valve_relay, valve_switch)
    pump = Pump(pump_relay)
    valve.valve_on()
    time.sleep(1)
    pump.pump_on()
    time.sleep(water_time)
    valve.valve_off()
    pump.pump_off()

@routes.route("/get-weather")
@login_required
def get_weather():
    latest_weather_data = ThreeHour.query.order_by(desc(ThreeHour.date)).first()
    json_response = request_weather()
    current_date, sunrise, sunset, weather_data = extract_data(json_response)
    if latest_weather_data:
        if latest_weather_data.date == current_date:
            flash("Todays data already exists", category="error")
        else:
            add_weather_to_db(current_date, sunrise, sunset, weather_data)
            flash("Added todays data", category="success")
    elif datetime.now().time().hour >= 22:
        flash("No available data for today", category="error")
    else:
        add_weather_to_db(current_date, sunrise, sunset, weather_data)
        flash("Added todays data", category="success")
    return redirect(url_for("routes.home"))

def add_weather_to_db(current_date, sunrise, sunset, weather_data):
    for wd in weather_data:
        time =          wd[0]
        temperature =   wd[1]
        humidity =      wd[2]
        weather =       wd[3]
        rain_chance =   wd[4]
        rain_recorded = wd[5]
        db.session.add(ThreeHour(date=current_date, time=time, temperature=temperature, humidity=humidity, weather=weather, rain_chance=rain_chance, rain_recorded=rain_recorded))
    db.session.add(Day(date=current_date, sunrise=sunrise, sunset=sunset))
    db.session.commit()

def kelvin_to_celsius(kelvin):
    return (kelvin - 273.15)

def request_weather():
    BASE_URL = "http://api.openweathermap.org/data/2.5/forecast?"
    with open("api.txt", "r") as f:
        API_KEY = f.read()
    LAT = "51.529"
    LON = "-3.191"
    url = BASE_URL + "lat=" + LAT + "&lon=" + LON + "&appid=" + API_KEY
    json_response = requests.get(url).json()
    return json_response

def extract_data(json):
    timezone = json["city"]["timezone"]
    sunrise = datetime.utcfromtimestamp(json["city"]["sunrise"] + timezone).time()
    sunset = datetime.utcfromtimestamp(json["city"]["sunset"] + timezone).time()
    current_date = datetime.now().date()
    weather_data = []
    for t_dict in json["list"]:
        date_time = datetime.utcfromtimestamp(t_dict["dt"] + timezone)
        if date_time.date() == current_date:
            temperature = round(kelvin_to_celsius(t_dict["main"]["temp"]), 2)
            humidity = t_dict["main"]["humidity"]
            weather = t_dict["weather"][0]["description"]
            rain_chance = t_dict["pop"]
            if "rain" in t_dict:
                rain_recorded = t_dict["rain"]["3h"]
            else:
                rain_recorded = 0
            weather_data.append((date_time.time(), temperature, humidity, weather, rain_chance, rain_recorded))
    return current_date, sunrise, sunset, weather_data

def format_for_graph(date):
    time_weather_labels = []
    temperature = []
    humidity = []
    rain_chance = []
    rain_recorded = []
    selected_three_hour = ThreeHour.query.filter(ThreeHour.date==date).order_by(ThreeHour.time).all()
    selected_day = Day.query.filter(Day.date==date).first()
    sunrise = selected_day.sunrise
    sunset = selected_day.sunset
    for each_three_hour in selected_three_hour:
        time_string = each_three_hour.time.strftime("%H:%M:%S")
        time_weather_label = f"{time_string} {each_three_hour.weather.title()}"
        time_weather_labels.append(time_weather_label)
        temperature.append(each_three_hour.temperature)
        humidity.append(each_three_hour.humidity)
        rain_chance.append(each_three_hour.rain_chance)
        rain_recorded.append(each_three_hour.rain_recorded)
    return sunrise, sunset, time_weather_labels, temperature, humidity, rain_chance, rain_recorded