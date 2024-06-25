from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class WaterForm(FlaskForm):
    duration = IntegerField("Time (Seconds)", validators=[DataRequired(), NumberRange(min=30, max=300, message="Minimum: %(min)s, Maximum: %(max)s")])
    submit = SubmitField("Water")


class CancelForm(FlaskForm):
    submit = SubmitField("Cancel")
