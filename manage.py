#!flask/bin/python
"""
Author: Swagger.pro
File: app.py
Purpose: runs the app!
"""

import os
from flask_script import Manager
from postmaster import app, db, models
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
    try:
        min_pw_length = models.Configs().from_json(
            {'setting': 'Minimum Password Length', 'value': '8'})
        db.session.add(min_pw_length)
    except:
        pass
    try:
        config_login_auditing = models.Configs().from_json(
            {'setting': 'Login Auditing', 'value': 'True'})
        db.session.add(config_login_auditing)
    except:
        pass
    try:
        config_maildb_auditing = models.Configs().from_json(
            {'setting': 'Mail Database Auditing', 'value': 'True'})
        db.session.add(config_maildb_auditing)
    except:
        pass
    try:
        config_log_path = models.Configs().from_json(
            {'setting': 'Log File', 'value': '../logs/postmaster.local'})
        db.session.add(config_log_path)
    except:
        pass
    try:
        disable_ldap_auth = models.Configs().from_json(
            {'setting': 'Enable LDAP Authentication', 'value': 'False'})
        db.session.add(disable_ldap_auth)
    except:
        pass
    try:
        ldap_server = models.Configs().from_json({'setting': 'AD Server LDAP String',
                                                  'value': 'LDAPS://postmaster.local:636'})
        db.session.add(ldap_server)
    except:
        pass
    try:
        domain = models.Configs().from_json({'setting': 'AD Domain', 'value': 'postmaster.local'})
        db.session.add(domain)
    except:
        pass
    try:
        ldap_admin_group = models.Configs().from_json(
            {'setting': 'AD PostMaster Group', 'value': 'PostMaster Admins'})
        db.session.add(ldap_admin_group)
    except:
        pass
    try:
        admin = models.Admins().from_json(
            {'username': 'user@postmaster.com', 'password': 'password', 'name': 'Default User'})
        db.session.add(admin)
    except:
        pass
    db.session.commit()


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


if __name__ == "__main__":
    manager.run()
