#!flask/bin/python
"""
Author: Swagger.pro
File: app.py
Purpose: runs the app!
"""

import os
from flask_script import Manager
from swagmail import app, db, models
from flask_migrate import Migrate, MigrateCommand

manager = Manager(app)
app.config.from_object('config')

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def createdb():
    '''Runs the db init, db migrate, db upgrade commands automatically'''
    os.system('python manage.py db init')
    os.system('python manage.py db migrate')
    os.system('python manage.py db upgrade')
    admin = models.Admins().from_json({'email': 'user@swagmail.com', 'password': 'password', 'name': 'Default User'})
    db.session.add(admin)
    config_login_auditing = models.Configs().from_json({'setting': 'Login Auditing', 'value': 'True'})
    db.session.add(config_login_auditing)
    config_maildb_auditing = models.Configs().from_json({'setting': 'Mail Database Auditing', 'value': 'True'})
    db.session.add(config_maildb_auditing)
    config_log_path = models.Configs().from_json({'setting': 'Log File', 'value': 'swagmail.log'})
    db.session.add(config_log_path)
    db.session.commit()


@manager.shell
def make_shell_context():
    ''' Returns app, db, models to the shell '''
    return dict(app=app, db=db, models=models)


@manager.command
def clean():
    '''Cleans the codebase'''

    if os.name == 'nt':
        commands = ["powershell.exe -Command \"@('*.pyc', '*.pyo', '*~', '__pycache__') |  Foreach-Object { Get-ChildItem -Filter $_ -Recurse | Remove-Item -Recurse -Force }\"", # pylint: disable=anomalous-backslash-in-string, line-too-long
                    "powershell.exe -Command \"@('swagmail.db', 'migrations') |  Foreach-Object { Get-ChildItem -Filter $_ | Remove-Item -Recurse -Force }\""] # pylint: disable=anomalous-backslash-in-string, line-too-long
    else:
        commands = ["find . -name '*.pyc' -exec rm -f {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "find . -name '*.pyo' -exec rm -f {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "find . -name '*~' -exec rm -f {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "find . -name '__pycache__' -exec rmdir {} \;",  # pylint: disable=anomalous-backslash-in-string
                    "rm -f swagmail.db"]
    for command in commands:
        os.system(command)


if __name__ == "__main__":
    manager.run()
