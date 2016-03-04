"""
Author: Swagger.pro
File: config.py
Purpose: config for the app
"""
from os import path


class BaseConfiguration(object):
    HOST_NAME = 'mail.swagger.pro'
    # Make this random (used to generate session keys)
    SECRET_KEY = 'e68bf2ea7a6494e65c9fbf2b7e652cf974281871713aa46c'
    basedir = path.abspath(path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'mysql://root:vagrant@localhost:3306/servermail'
    SQLALCHEMY_MIGRATE_REPO = path.join(basedir, 'db_repository')


class TestConfiguration(BaseConfiguration):
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True


class DevConfiguration(BaseConfiguration):
    basedir = path.abspath(path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, 'postmaster.db')
    DEBUG = True
