"""Executes application."""
import logging
from app import create_app

# Creates configured flask application object.
app = create_app()

# Executes locally if run directly.
if __name__ == "__main__":
    app.run(host="0.0.0.0")
else:
    # TODO test gunicorn with linux
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
