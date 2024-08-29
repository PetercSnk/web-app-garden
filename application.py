"""Executes application."""
import logging
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.logger = logging.getLogger("development")
    app.run(host="0.0.0.0", port=5000)
else:
    app.logger = logging.getLogger("production")
