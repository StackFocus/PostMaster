"""
Author: StackFocus
File: config.py
Purpose: config for the app
"""
from os import path


class BaseConfiguration(object):
    # We disable CSRF because it interferes with logging in
    # from anywhere but the form on the login page.
    # We introduce very little risk by disabling this.
    WTF_CSRF_ENABLED = False
    # Make this random (used to generate session keys)
    SECRET_KEY = 'e9987dce48df3ce98542529fd074d9e9f9cd40e66fc6c4c2'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:vagrant@localhost:3306/servermail'
    basedir = path.abspath(path.dirname(__file__))
    SQLALCHEMY_MIGRATE_REPO = path.join(basedir, 'db/migrations')
    LOG_LOCATION = '/opt/postmaster/logs/postmaster.log'


class TestConfiguration(BaseConfiguration):
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True


class DevConfiguration(BaseConfiguration):
    WTF_CSRF_ENABLED = False
    DEBUG = True
