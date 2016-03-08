"""
Author: Swagger.pro
File: config.py
Purpose: config for the app
"""
from os import path


class BaseConfiguration(object):
    HOST_NAME = 'mail.swagger.pro'
    # Make this random (used to generate session keys)
    SECRET_KEY = '1c11d7ec3eb95e6ddb497d792452ced7ab2f3f0e41d11a20'
    basedir = path.abspath(path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'mysql://root:vagrant@localhost:3306/servermail'
    SQLALCHEMY_MIGRATE_REPO = path.join(basedir, 'db_repository')


class TestConfiguration(BaseConfiguration):
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True


class DevConfiguration(BaseConfiguration):
    DEBUG = True
