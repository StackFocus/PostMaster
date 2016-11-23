"""
Author: StackFocus
File: __init__.py
Purpose: initializes the application
"""

from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

__version__ = 'v1.1.0.0'
app = Flask(__name__)

if environ.get('POSTMASTER_DEV') == 'TRUE':
    app.config.from_object('config.DevConfiguration')
else:
    app.config.from_object('config.BaseConfiguration')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

from postmaster.apiv1 import apiv1
from postmaster.views.common import common
app.register_blueprint(apiv1)
app.register_blueprint(common)

from postmaster import models
