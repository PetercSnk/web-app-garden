from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TimeField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class PlantForm(FlaskForm):
    """Creation of new plant."""
    name = StringField("Name", validators=[DataRequired(), Length(max=10)])
    description = StringField("Description", validators=[DataRequired(), Length(max=50)])
    system = SelectField("System", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Create")


class WaterForm(FlaskForm):
    """Get duration in seconds for watering plant."""
    duration_sec = IntegerField("Time (Seconds)", validators=[DataRequired(), NumberRange(min=30, max=300, message="Minimum: %(min)s, Maximum: %(max)s")])
    submit = SubmitField("Water")


class ConfigForm(FlaskForm):
    """Edit values for plant configuration."""
    enabled = BooleanField("Enable Automatic Watering")
    duration_sec = IntegerField("Water Duration (Seconds)", validators=[DataRequired(), NumberRange(min=30, max=300, message="Minimum: %(min)s, Maximum: %(max)s")])
    occurrence_days = IntegerField("Occurrence (Days)", validators=[DataRequired(), NumberRange(min=1)])
    mode = SelectField("Mode", choices=[(1, "Sunset"), (2, "Sunrise"), (3, "Default")], validators=[DataRequired()])
    default = TimeField("Default Water Time", validators=[DataRequired()])
    rain_reset = BooleanField("Reset Timer on Rainfall")
    submit = SubmitField("Save")
