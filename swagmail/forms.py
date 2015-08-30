from flask_wtf import Form
from wtforms import StringField, HiddenField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(Form):
    username = StringField(
        label="Username: ",
        validators=[DataRequired()]
    )
    password = PasswordField(
        label="Password: ",
        validators=[DataRequired()]
    )
