"""
Author: StackFocus
File: config.py
Purpose: config for the app
"""
from os import path

basedir = path.abspath(path.dirname(__file__))


class BaseConfiguration(object):
    # We disable CSRF because it interferes with logging in
    # from anywhere but the form on the login page.
    # We introduce very little risk by disabling this.
    WTF_CSRF_ENABLED = False
    # Make this random (used to generate session keys)
    SECRET_KEY = '123456789abcdef123456789'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:vagrant@localhost:3306/servermail'
    LOG_LOCATION = '/opt/postmaster/logs/postmaster.log'


class TestConfiguration(BaseConfiguration):
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    LOG_LOCATION = ''


class DevConfiguration(BaseConfiguration):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(
        path.join(basedir, 'postmaster.db'))
    WTF_CSRF_ENABLED = False
    DEBUG = True
