"""Routes for the weather module."""
from datetime import datetime
from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.weather.models import Daily, Hourly
from app.weather import weather_bp, jobs


@weather_bp.route("/", methods=["GET"])
@login_required
def index():
    """Checks what daily records exist and redirects accordingly.

    Will redirect to either todays date, the first available record, or nothing.
    """
    daily_today = Daily.query.filter(Daily.date == datetime.now().date()).first()
    if daily_today:
        return redirect(url_for("weather_bp.graph", daily_id=daily_today.id))
    else:
        daily_first = Daily.query.first()
        if daily_first:
            return redirect(url_for("weather_bp.graph", daily_id=daily_first.id))
        else:
            return redirect(url_for("weather_bp.graph", daily_id=0))


@weather_bp.route("/request-weather", methods=["GET"])
@login_required
def request_weather():
    daily_count, hourly_count = jobs.get_weather()
    msg = f"Added {daily_count} / {hourly_count} new records"
    flash(msg, category="info")
    return redirect(url_for("weather_bp.index"))


@weather_bp.route("/<int:daily_id>", methods=["GET"])
@login_required
def graph(daily_id):
    """Handles daily weather charts and requests for weather data."""
    if request.method == "GET":
        available = Daily.query.order_by(Daily.date).all()
        if daily_id in [record.id for record in available]:
            daily_data = Daily.query.filter(Daily.id == daily_id).first()
            hourly_data = get_formatted_hourly(daily_id)
            return render_template("weather/weather.html",
                                   render=True,
                                   user=current_user,
                                   available=available,
                                   city=current_app.config["CITY"],
                                   region=current_app.config["REGION"],
                                   daily_data=daily_data,
                                   hourly_data=hourly_data)
        else:
            return render_template("weather/weather.html",
                                   render=False,
                                   user=current_user,
                                   available=available)


def get_formatted_hourly(daily_id):
    """Retieves and formats all hourly data for the given daily id."""
    hourly = Hourly.query.filter(Hourly.daily_id == daily_id).order_by(Hourly.time).all()
    data = {
        "time": [],
        "temperature": [],
        "humidity": [],
        "precipitation_probability": [],
        "precipitation": []
    }
    for record in hourly:
        data["time"].append(f"{record.time.strftime('%H:%M')}")
        data["temperature"].append(record.temperature)
        data["humidity"].append(record.humidity)
        data["precipitation_probability"].append(record.precipitation_probability)
        data["precipitation"].append(record.precipitation)
    return data


@weather_bp.context_processor
def utility():
    """Context processors for use within html templates."""
    def format_date(datetime_obj):
        """Formats datetime objects into readable format."""
        return datetime_obj.strftime("%d-%b")
    return dict(format_date=format_date)
