﻿#!flask/bin/python
"""
Author: StackFocus
File: manage.py
Purpose: Manages the app
"""

import os
import fileinput
import flask_migrate
from re import sub
from flask_script import Manager
from postmaster import app, db, models
from postmaster.utils import add_default_configuration_settings

manager = Manager(app)
if os.environ.get('POSTMASTER_DEV'):
    app.config.from_object('config.DevConfiguration')
else:
    app.config.from_object('config.BaseConfiguration')

migrate = flask_migrate.Migrate(app, db)

manager = Manager(app)
manager.add_command('db', flask_migrate.MigrateCommand)


@manager.command
def createdb():
    """Runs the db init, db migrate, db upgrade commands automatically,
    and adds the default configuration settings if they are missing"""
    if not os.path.isdir('migrations'):
        flask_migrate.init()
        flask_migrate.migrate()
    flask_migrate.upgrade()
    add_default_configuration_settings()


@manager.command
def existingdb():
    """Only use this function if you setup your mailserver
    database before this application and only have the virtual_* tables.

    It marks the first revision complete, which
    is the revision that creates the virtual_* tables

    If you run this command down the road, it will error on
    the next revision e8f52e92abd0 where it creates the postmaster tables.
    You'll have to stamp the database to the latest revision.
    `python manage.py db stamp head`
    """
    flask_migrate.stamp(revision='bcc85aaa7896')
    flask_migrate.upgrade()
    add_default_configuration_settings()


@manager.command
def upgradedb():
    """Upgrades the existing database to new state and adds
    default configurations if missing"""
    flask_migrate.upgrade()
    add_default_configuration_settings()


@manager.shell
def make_shell_context():
    """Returns app, db, models to the shell"""
    return dict(app=app, db=db, models=models)


@manager.command
def clean():
    """Cleans the codebase, including database migration scripts"""
    if os.name == 'nt':
        commands = ["powershell.exe -Command \"@('*.pyc', '*.pyo', '*~', '__pycache__') |  Foreach-Object { Get-ChildItem -Filter $_ -Recurse | Remove-Item -Recurse -Force }\"",  # pylint: disable=anomalous-backslash-in-string, line-too-long
                    "powershell.exe -Command \"@('postmaster.db', 'db', 'postmaster.log') |  Foreach-Object { Get-ChildItem -Filter $_ | Remove-Item -Recurse -Force }\""]  # pylint: disable=anomalous-backslash-in-string, line-too-long
    else:
        commands = ["find . -name '*.pyc' -exec rm -f {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "find . -name '*.pyo' -exec rm -f {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "find . -name '*~' -exec rm -f {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "find . -name '__pycache__' -exec rmdir {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "rm -f postmaster.db postmaster.log",
                    "rm -rf db"]
    for command in commands:
        os.system(command)


@manager.command
def generatekey():
    """Replaces the SECRET_KEY in config.py with a new random one"""
    for line in fileinput.input('config.py', inplace=True):
        print(sub(r'(?<=SECRET_KEY = \')(.+)(?=\')', os.urandom(24).encode('hex'), line.rstrip()))


@manager.command
def setdburi(uri):
    """Replaces the BaseConfiguration SQLALCHEMY_DATABASE_URI in config.py with one supplied"""
    base_config_set = False
    for line in fileinput.input('config.py', inplace=True, backup='.bak'):
        if not base_config_set and 'SQLALCHEMY_DATABASE_URI' in line:
            print(sub(r'(?<=SQLALCHEMY_DATABASE_URI = \')(.+)(?=\')', uri, line.rstrip()))
            base_config_set = True
        else:
            print(line.rstrip())


@manager.command
def setlogfile(filepath):
    """Replaces the BaseConfiguration LOG_LOCATION in config.py with one supplied"""
    base_config_set = False
    for line in fileinput.input('config.py', inplace=True, backup='.bak'):
        if not base_config_set and 'LOG_LOCATION' in line:
            print(sub(r'(?<=LOG_LOCATION = \')(.+)(?=\')', filepath, line.rstrip()))
            base_config_set = True
        else:
            print(line.rstrip())

if __name__ == "__main__":
    manager.run()
