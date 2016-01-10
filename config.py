"""
Author: Swagger.pro
File: config.py
Purpose: config for the app
"""
from os import path

HOST_NAME = 'mail.swagger.pro'
# Make this random (used to generate session keys)
SECRET_KEY = '73Sjkadas%hASDe45@1238Due12jdodjfFDweq82348*(#89asdasdas'
basedir = path.abspath(path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, 'swagmail.db')
SQLALCHEMY_MIGRATE_REPO = path.join(basedir, 'db_repository')

""" Dev """
DEBUG = True
