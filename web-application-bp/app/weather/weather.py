from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.weather.models import Daily, Hourly
from app.weather import weather_bp, jobs
from datetime import datetime


@weather_bp.route("/", methods=["GET"])
@login_required
def index():
    daily_today = Daily.query.filter(Daily.date == datetime.now().date()).first()
    if daily_today:
        # redirect to todays id if it exists in db
        return redirect(url_for("weather_bp.graph", daily_id=daily_today.id))
    else:
        daily_first = Daily.query.first()
        if daily_first:
            # redirect to some other id that exists if today is not in db
            return redirect(url_for("weather_bp.graph", daily_id=daily_first.id))
        else:
            # if nothing exists in db redirect with any value for daily_id, the graph won't render regardless due to check in graph function
            return redirect(url_for("weather_bp.graph", daily_id=0))


@weather_bp.route("/<int:daily_id>", methods=["GET", "POST"])
@login_required
def graph(daily_id):
    if request.method == "POST":
        if "get-weather" in request.form:
            current_app.logger.debug("Getting weather")
            daily_count, hourly_count = jobs.get_weather()
            msg = f"Added {daily_count} & {hourly_count} new records"
            flash(msg, category="info")
            return redirect(url_for("weather_bp.index"))
    elif request.method == "GET":
        daily_all = Daily.query.order_by(Daily.date).all()
        if daily_id in [daily.id for daily in daily_all]:
            daily = Daily.query.filter(Daily.id == daily_id).first()
            time, temperature, humidity, precipitation_probability, precipitation = format(daily_id)
            return render_template("weather/weather.html",
                                   render=True,
                                   user=current_user,
                                   daily_all=daily_all,
                                   date=daily.date,
                                   sunrise=daily.sunrise,
                                   sunset=daily.sunset,
                                   description=daily.weather_description,
                                   time=time,
                                   temperature=temperature,
                                   humidity=humidity,
                                   precipitation_probability=precipitation_probability,
                                   precipitation=precipitation)
        else:
            flash("No Data", category="info")
        return render_template("weather/weather.html", render=False, user=current_user)


def format(daily_id):
    hourly_all = Hourly.query.filter(Hourly.daily_id == daily_id).order_by(Hourly.time).all()
    time, temperature, humidity, precipitation_probability, precipitation = [], [], [], [], []
    for hourly in hourly_all:
        time.append(f"{hourly.time.strftime('%H:%M')}")
        temperature.append(hourly.temperature)
        humidity.append(hourly.humidity)
        precipitation_probability.append(hourly.precipitation_probability)
        precipitation.append(hourly.precipitation)
    return time, temperature, humidity, precipitation_probability, precipitation


@weather_bp.context_processor
def utility():
    def format_date(datetime_obj):
        return datetime_obj.strftime("%d-%b")
    return dict(format_date=format_date)
