"""Executes application."""
import logging
from app import create_app

app = create_app()

if __name__ == "__main__":
    # ???
    # development_logger = logging.getLogger("development")
    # app.logger.setLevel(development_logger.level)
    # app.logger.handlers = development_logger.handlers
    # app.logger = logging.getLogger("development")
    app.run(host="0.0.0.0", port=5000)
