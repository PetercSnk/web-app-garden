"""All forms used by the water module."""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TimeField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class PlantForm(FlaskForm):
    """Form to retrieve details for new plant entries.

    The select field for systems contains only classes that
    are specified within the systems.py file.
    """
    name = StringField("Name",
                       validators=[DataRequired(),
                                   Length(max=10)])
    description = StringField("Description",
                              validators=[DataRequired(),
                                          Length(max=50)])
    system = SelectField("System",
                         coerce=int,
                         validators=[DataRequired()])
    submit = SubmitField("Create")


class WaterForm(FlaskForm):
    """Form to retrieve an integer corresponding to a time in seconds.

    This is used for the manual watering of plants.
    """
    duration_sec = IntegerField("Time (Seconds)",
                                validators=[DataRequired(),
                                            NumberRange(min=30,
                                                        max=300,
                                                        message="Minimum: %(min)s, Maximum: %(max)s")])
    submit = SubmitField("Water")


class ConfigForm(FlaskForm):
    """Form to retreive new configs for existing plants."""
    enabled = BooleanField("Enable Automatic Watering")
    duration_sec = IntegerField("Water Duration (Seconds)",
                                validators=[DataRequired(),
                                            NumberRange(min=30,
                                                        max=300,
                                                        message="Minimum: %(min)s, Maximum: %(max)s")])
    occurrence_days = IntegerField("Occurrence (Days)",
                                   validators=[DataRequired(),
                                               NumberRange(min=1)])
    mode = SelectField("Mode",
                       choices=[(1, "Sunset"), (2, "Sunrise"), (3, "Default")],
                       coerce=int,
                       validators=[DataRequired()])
    default = TimeField("Default Water Time",
                        validators=[DataRequired()])
    rain_reset = BooleanField("Postpone on Rainfall")
    threshold_mm = IntegerField("Volume of Rainfall Threshold (Millimetres)",
                                validators=[DataRequired()])
    submit = SubmitField("Save")
