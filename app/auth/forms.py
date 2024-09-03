"""All forms used by the auth module."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Form to retrieve users details for authentication."""
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class AdminForm(FlaskForm):
    """Form to update users details."""
    username = StringField("Username")
    password = PasswordField("Password")
    submit = SubmitField("Update")
