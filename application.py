"""Executes application."""
import os
import logging
from app import create_app

# Create logs directory before building application when running directly
if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__))
    logsdir = os.path.join(basedir, "logs")
    if not os.path.exists(logsdir):
        os.makedirs(logsdir)

app = create_app()

if __name__ == "__main__":
    app.logger = logging.getLogger("development")
    app.run(host="0.0.0.0", port=5000)
else:
    app.logger = logging.getLogger("production")
