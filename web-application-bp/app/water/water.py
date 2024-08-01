"""Routes for the water module."""
from flask import render_template, flash, current_app, redirect, url_for, request
from flask_login import login_required, current_user
from app.water.models import Config, Plant, System
from app.water.forms import WaterForm, ConfigForm, PlantForm
from app.water.jobs import process, remove_job, schedule_job, get_due_date
from app.water import water_bp
from app import db, events, scheduler
from threading import Event
from datetime import datetime


@water_bp.route("/setup", methods=["GET", "POST"])
@login_required
def setup():
    """Create plants and assign a default config and event obj."""
    plant_form = PlantForm()
    systems_in_use = [plant.system.id for plant in Plant.query.all()]
    systems_available = []
    for system in System.query.all():
        if system.id not in systems_in_use:
            systems_available.append((system.id, system.name))
    current_app.logger.debug(f"Systems available {systems_available}")
    if not systems_available:
        flash("No systems available", category="info")
    plant_form.system.choices = systems_available
    if request.method == "POST" and plant_form.validate():
        name = plant_form.name.data
        new_config = Config(enabled=False,
                            duration_sec=120,
                            occurrence_days=1,
                            mode=3,
                            default=datetime.strptime("6", "%H").time(),
                            rain_reset=False,
                            threshold_mm=1,
                            last_edit=datetime.now().replace(microsecond=0))
        new_plant = Plant(system_id=plant_form.system.data,
                          name=name,
                          description=plant_form.description.data,
                          status=False,
                          config=new_config)
        events[name] = Event()
        db.session.add(new_plant)
        db.session.commit()
        current_app.logger.debug(f"New plant '{name}' created")
    plants_available = Plant.query.order_by(Plant.id).all()
    return render_template("water/setup.html",
                           user=current_user,
                           plant_form=plant_form,
                           plants_available=plants_available)


@water_bp.route("/delete/<int:plant_id>", methods=["GET", "POST"])
@login_required
def delete(plant_id):
    """Delete plants and all relationships."""
    plant_selected = Plant.query.filter(Plant.id == plant_id).first()
    if plant_selected:
        flash("Deleted plant", category="success")
        events.pop(plant_selected.name)
        remove_job(plant_selected.id)
        db.session.delete(plant_selected)
        db.session.commit()
        current_app.logger.debug(f"Deleted plant '{plant_selected.name}'")
    else:
        flash("Does not exist", category="error")
    return redirect(url_for("water_bp.setup"))


@water_bp.route("/configure/<int:plant_id>", methods=["GET", "POST"])
@login_required
def configure(plant_id):
    """Edit plant config settings."""
    plant_selected = Plant.query.filter(Plant.id == plant_id).first()
    if plant_selected:
        config_form = ConfigForm()
        if request.method == "POST" and config_form.validate():
            # remove existing jobs when config is updated
            remove_job(plant_selected.id)
            now = datetime.now().replace(microsecond=0)
            plant_selected.config.enabled = config_form.enabled.data
            plant_selected.config.duration_sec = config_form.duration_sec.data
            plant_selected.config.occurrence_days = config_form.occurrence_days.data
            plant_selected.config.mode = config_form.mode.data
            plant_selected.config.default = config_form.default.data
            plant_selected.config.rain_reset = config_form.rain_reset.data
            plant_selected.config.threshold_mm = config_form.threshold_mm.data
            plant_selected.config.last_edit = now
            if plant_selected.config.enabled:
                plant_selected.config.job_init = now
                plant_selected.config.job_due = get_due_date(plant_selected.config)
                schedule_job(plant_selected)
            db.session.commit()
            current_app.logger.debug(f"Config for '{plant_selected.name}' updated")
        # prefill forms with current configuration
        config_form.enabled.default = plant_selected.config.enabled
        config_form.duration_sec.default = plant_selected.config.duration_sec
        config_form.occurrence_days.default = plant_selected.config.occurrence_days
        config_form.mode.default = plant_selected.config.mode
        config_form.default.default = plant_selected.config.default
        config_form.rain_reset.default = plant_selected.config.rain_reset
        config_form.threshold_mm.default = plant_selected.config.threshold_mm
        config_form.process()
        active_job = scheduler.get_job(f"auto_water{plant_selected.id}")
        plants_available = Plant.query.order_by(Plant.id).all()
        return render_template("water/configure.html",
                               user=current_user,
                               plant_selected=plant_selected,
                               config_form=config_form,
                               plants_available=plants_available,
                               active_job=active_job)
    else:
        flash("Does not exist", category="error")
        return redirect(url_for("water_bp.configure_check"))


@water_bp.context_processor
def utility():
    def format_date(datetime_obj):
        if datetime_obj:
            return datetime_obj.strftime("%d-%b %H:%M:%S")
        else:
            return ""
    return dict(format_date=format_date)


@water_bp.route("/configure/check", methods=["GET"])
@login_required
def configure_check():
    """Check if plants exist and redirect accordingly."""
    plant = Plant.query.first()
    if plant:
        return redirect(url_for("water_bp.configure", plant_id=plant.id))
    else:
        flash("Must create plant to access configure options", category="error")
        return redirect(url_for("water_bp.setup"))


@water_bp.route("/water/<int:plant_id>", methods=["GET", "POST"])
@login_required
def water(plant_id):
    """Create new thread and start watering process."""
    plant_selected = Plant.query.filter(Plant.id == plant_id).first()
    if plant_selected:
        water_form = WaterForm()
        if request.method == "POST" and water_form.validate():
            if plant_selected.status:
                flash("Already Runnning", category="error")
            else:
                job_name = f"manual_water{plant_selected.id}"
                scheduler.add_job(func=process,
                                  id=job_name,
                                  name=job_name,
                                  args=[water_form.duration_sec.data, plant_selected.id])
                current_app.logger.debug("Started manual water process")
                flash("Started Process", category="success")
        plants_available = Plant.query.order_by(Plant.id).all()
        return render_template("water/water.html",
                               user=current_user,
                               plant_selected=plant_selected,
                               water_form=water_form,
                               plants_available=plants_available)
    else:
        flash("Does not exist", category="error")
        return redirect(url_for("water_bp.water_check"))


@water_bp.route("/water/check", methods=["GET"])
@login_required
def water_check():
    """Check if plants exist and redirect accordingly."""
    plant = Plant.query.first()
    if plant:
        return redirect(url_for("water_bp.water", plant_id=plant.id))
    else:
        flash("Must create plant to access water options", category="error")
        return redirect(url_for("water_bp.setup"))


@water_bp.route("/cancel/<int:plant_id>", methods=["GET", "POST"])
@login_required
def cancel(plant_id):
    """Cancel watering process in thread created by water."""
    plant_selected = Plant.query.filter(Plant.id == plant_id).first()
    if plant_selected:
        if plant_selected.status:
            events[plant_selected.name].set()
            current_app.logger.debug(f"Set event for '{plant_selected.name}'")
            flash("Stopped Process", category="success")
        else:
            flash("Not Running", category="error")
        return redirect(url_for("water_bp.water", plant_id=plant_selected.id))
    else:
        flash("Does not exist", category="error")
        return redirect(url_for("water_bp.water_check"))
