from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.weather.models import Weather, Day
from datetime import datetime
from app.weather import weather_bp, jobs


@weather_bp.route("/", methods=["GET"])
@login_required
def index():
    today = datetime.now().date()
    day = Day.query.filter(Day.date == today).first()
    if day:
        # redirect to todays id if it exists in db
        return redirect(url_for("weather_bp.graph", day_id=day.id))
    else:
        day = Day.query.first()
        if day:
            # redirect to some other id that exists if today is not in db
            return redirect(url_for("weather_bp.graph", day_id=day.id))
        else:
            # if nothing exists in db redirect with any value for day_id, the graph won't render regardless due to check in graph function
            return redirect(url_for("weather_bp.graph", day_id=0))


@weather_bp.route("/<int:day_id>", methods=["GET", "POST"])
@login_required
def graph(day_id):
    if request.method == "POST":
        if "get-weather" in request.form:
            current_app.logger.debug("Getting weather")
            msg = jobs.get_weather()
            flash(msg, category="info")
            return redirect(url_for("weather_bp.graph", day_id=day_id))
    elif request.method == "GET":
        days = Day.query.order_by(Day.date).all()
        if day_id in [day.id for day in days]:
            date, sunrise, sunset, labels, temperature_c, humidity, rain_probability, rain_volume_mm = format(day_id)
            return render_template("weather/weather.html", render=True, user=current_user, days=days, date=date, sunrise=sunrise, sunset=sunset, labels=labels, temperature_c=temperature_c, humidity=humidity, rain_probability=rain_probability, rain_volume_mm=rain_volume_mm)
        else:
            flash("No Data", category="info")
            return render_template("weather/weather.html", render=False, user=current_user)


def format(day_id):
    day = Day.query.filter(Day.id == day_id).first()
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
