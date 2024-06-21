from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class WaterForm(FlaskForm):
    water_time = IntegerField("Time (Seconds)", validators=[DataRequired(), NumberRange(min=30, max=300, message="Minimum: %(min)s, Maximum: %(max)s")])
    water_submit = SubmitField("Water")


class CancelForm(FlaskForm):
    cancel_submit = SubmitField("Cancel")
