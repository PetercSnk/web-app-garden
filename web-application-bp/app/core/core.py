from flask import redirect, url_for
from app import scheduler
from app.core import core_bp
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_ADDED, EVENT_JOB_REMOVED


@core_bp.route("/", methods=["GET"])
def core_index():
    """Redirect to main access point."""
    return redirect(url_for("auth_bp.login"))


def job_added(event):
    """Job added callback."""
    with scheduler.app.app_context():
        job = scheduler.get_job(event.job_id)
        scheduler.app.logger.debug(f"Added job '{job.id}' @ {job.next_run_time}")


def job_removed(event):
    """Job removed callback."""
    with scheduler.app.app_context():
        scheduler.app.logger.debug(f"Removed job '{event.job_id}'")


def job_executed(event):
    """Job executed callback."""
    with scheduler.app.app_context():
        scheduler.app.logger.debug(f"Executed job '{event.job_id}'")


def job_error(event):
    """Job error callback."""
    with scheduler.app.app_context():
        scheduler.app.logger.debug(f"Error with job '{event.job_id}'")


scheduler.add_listener(job_added, EVENT_JOB_ADDED)
scheduler.add_listener(job_removed, EVENT_JOB_REMOVED)
scheduler.add_listener(job_executed, EVENT_JOB_EXECUTED)
scheduler.add_listener(job_error, EVENT_JOB_ERROR)
