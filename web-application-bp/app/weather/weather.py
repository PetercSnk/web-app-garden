from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.weather.models import Weather, Day
from datetime import datetime
from app.core import jobs
from app.weather import weather_bp


@weather_bp.route("/", methods=["GET"])
@login_required
def index():
    today = datetime.now().date()
    db_today = Day.query.filter(Day.date == today).one()
    if db_today:
        # redirect to todays id if it exists in db
        return redirect(url_for("weather.weather", day_id=db_today.id))
    else:
        db_first = Day.query.first()
        if db_first:
            # redirect to some other id that exists if today is not in db
            return redirect(url_for("weather.weather", day_id=db_first.id))
        else:
            # if nothing exists in db redirect to /0
            return redirect(url_for("weather.weather", day_id=0))


@weather_bp.route("/<int:day_id>", methods=["GET", "POST"])
@login_required
def weather(day_id):
    if request.method == "POST":
        if "get-weather" in request.form:
            msg = jobs.get_weather()
            flash(msg, category="info")
            return redirect(url_for("weather.weather", day_id=day_id))
    else:
        db_days = Day.query.order_by(Day.date).all()
        if day_id > 0:
            date, sunrise, sunset, labels, temperature_c, humidity, rain_probability, rain_volume_mm = format_for_graph(day_id)
            return render_template("weather.html", user=current_user, db_days=db_days, date=date, sunrise=sunrise, sunset=sunset, labels=labels, temperature_c=temperature_c, humidity=humidity, rain_probability=rain_probability, rain_volume_mm=rain_volume_mm)
        else:
            return render_template("weather.html", user=current_user, db_days=db_days, date=None, sunrise=None, sunset=None, labels=0, temperature_c=0, humidity=0, rain_probability=0, rain_volume_mm=0)


def format_for_graph(day_id):
    day = Day.query.filter(Day.id == day_id).one()
    weather = Weather.query.filter(Weather.day_id == day.id).order_by(Weather.time).all()
    labels, temperature_c, humidity, rain_probability, rain_volume_mm = [], [], [], [], []
    for three_hour_step in weather:
        labels.append(f"{three_hour_step.time.strftime('%H:%M')} {three_hour_step.description.title()}")
        temperature_c.append(three_hour_step.temperature_c)
        humidity.append(three_hour_step.humidity)
        rain_probability.append(three_hour_step.rain_probability)
        rain_volume_mm.append(three_hour_step.rain_volume_mm)
    return day.date, day.sunrise, day.sunset, labels, temperature_c, humidity, rain_probability, rain_volume_mm


@weather_bp.context_processor
def utility():
    def format_date(datetime_obj):
        return datetime_obj.strftime("%d-%b")
    return dict(format_date=format_date)
