"""
Author: Swagger.pro
File: config.py
Purpose: config for the app
"""
from os import path


class BaseConfiguration(object):
    HOST_NAME = 'mail.swagger.pro'
    # Make this random (used to generate session keys)
    SECRET_KEY = 'e9987dce48df3ce98542529fd074d9e9f9cd40e66fc6c4c2'
    basedir = path.abspath(path.dirname(__file__))
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:vagrant@localhost:3306/servermail'
    SQLALCHEMY_MIGRATE_REPO = path.join(basedir, 'db_repository')


class TestConfiguration(BaseConfiguration):
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True


class DevConfiguration(BaseConfiguration):
    DEBUG = True
