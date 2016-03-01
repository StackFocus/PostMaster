#!flask/bin/python
"""
Author: Swagger.pro
File: app.py
Purpose: runs the app!
"""

import os
import fileinput
from re import sub, match
from flask_script import Manager
from postmaster import app, db, models
from postmaster.utils import add_default_configuration_settings
from flask_migrate import Migrate, MigrateCommand

manager = Manager(app)
app.config.from_object('config.BaseConfiguration')

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def createdb():
    """Runs the db init, db migrate, db upgrade commands automatically"""
    os.system('python manage.py db init')
    os.system('python manage.py db migrate')
    os.system('python manage.py db upgrade')
    add_default_configuration_settings()


@manager.shell
def make_shell_context():
    """Returns app, db, models to the shell"""
    return dict(app=app, db=db, models=models)


@manager.command
def clean():
    """Cleans the codebase"""

    if os.name == 'nt':
        commands = ["powershell.exe -Command \"@('*.pyc', '*.pyo', '*~', '__pycache__') |  Foreach-Object { Get-ChildItem -Filter $_ -Recurse | Remove-Item -Recurse -Force }\"",  # pylint: disable=anomalous-backslash-in-string, line-too-long
                    "powershell.exe -Command \"@('postmaster.db', 'migrations', 'postmaster.log') |  Foreach-Object { Get-ChildItem -Filter $_ | Remove-Item -Recurse -Force }\""]  # pylint: disable=anomalous-backslash-in-string, line-too-long
    else:
        commands = ["find . -name '*.pyc' -exec rm -f {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "find . -name '*.pyo' -exec rm -f {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "find . -name '*~' -exec rm -f {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "find . -name '__pycache__' -exec rmdir {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "rm -f postmaster.db postmaster.log",
                    "rm -rf migrations"]
    for command in commands:
        os.system(command)


@manager.command
def generatekey():
    """Replaces the SECRET_KEY in config.py with a new random one"""
    for line in fileinput.input('config.py', inplace=True):
        print(sub(r'(?<=SECRET_KEY = \')(.+)(?=\')', os.urandom(24).encode('hex'), line.rstrip()))


if __name__ == "__main__":
    manager.run()
