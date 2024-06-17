from app import create_app
import logging

app = create_app()

if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(levelname)s | %(name)s %(threadName)s >>> %(message)s")
    app.run(host="0.0.0.0")
else:
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
