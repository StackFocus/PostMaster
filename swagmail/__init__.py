"""
Author: Swagger.pro
File: __init__.py
Purpose: initializes the application
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

from apiv1 import apiv1
from views.common import common
app.register_blueprint(apiv1)
app.register_blueprint(common)

from swagmail import models
