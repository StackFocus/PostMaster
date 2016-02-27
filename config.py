"""
Author: Swagger.pro
File: config.py
Purpose: config for the app
"""
from os import path


class BaseConfiguration(object):
    HOST_NAME = 'mail.swagger.pro'
    # Make this random (used to generate session keys)
    SECRET_KEY = '73Sjkadas%hASDe45@1238Due12jdodjfFDweq82348*(#89asdasdas'
    basedir = path.abspath(path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        path.join(basedir, 'postmaster.db')
    SQLALCHEMY_MIGRATE_REPO = path.join(basedir, 'db_repository')


class TestConfiguration(BaseConfiguration):
    TESTING = True
    WTF_CSRF_ENABLED = False

    # + join(_cwd, 'testing.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Since we want our unit tests to run quickly
    # we turn this down - the hashing is still done
    # but the time-consuming part is left out.
