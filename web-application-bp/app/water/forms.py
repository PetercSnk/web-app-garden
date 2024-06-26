from flask_wtf import FlaskForm
from wtforms import IntegerField, TimeField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class WaterForm(FlaskForm):
    duration_sec = IntegerField("Time (Seconds)", validators=[DataRequired(), NumberRange(min=30, max=300, message="Minimum: %(min)s, Maximum: %(max)s")])
    submit = SubmitField("Water")


class CancelForm(FlaskForm):
    submit = SubmitField("Cancel")


class AutoForm(FlaskForm):
    enabled = BooleanField("Enable Automatic Watering", validators=[DataRequired()])
    duration_sec = IntegerField("Water Duration (Seconds)", validators=[DataRequired(), NumberRange(min=30, max=300, message="Minimum: %(min)s, Maximum: %(max)s")])
    min_wait_hr = IntegerField("Minimum Wait (Hours)", validators=[DataRequired()])
    mode = IntegerField("Mode (1:Sunset, 2:Sunrise, 3:Custom)", validators=[DataRequired(), NumberRange(min=1, max=3, message="Modes only 1, 2, and 3 are available")])
    time = TimeField("Custom Water Time", validators=[DataRequired()])
    rain_reset = BooleanField("Reset Timer on Rainfall", validators=[DataRequired()])
    submit = SubmitField("Save")
