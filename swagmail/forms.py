"""
Author: Swagger.pro
File: forms.py
Purpose: form definitions for the app
"""

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(Form):
    """
    Class for login form on /login
    """

    username = StringField(
        label="Username: ",
        validators=[DataRequired()]
    )
    password = PasswordField(
        label="Password: ",
        validators=[DataRequired()]
    )
