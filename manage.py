#!flask/bin/python
"""
Author: StackFocus
File: manage.py
Purpose: Manages the app
"""

import flask_migrate
from fileinput import input
from os import path, walk, remove, urandom
from shutil import rmtree
from re import sub, compile
from flask_script import Manager
from postmaster import app, db, models, __version__
from postmaster.utils import add_default_configuration_settings, clear_lockout_fields_on_user, reset_admin_password

migrate = flask_migrate.Migrate(app, db)

manager = Manager(app)
manager.add_command('db', flask_migrate.MigrateCommand)


@manager.command
def upgradedb():
    """Upgrades the existing database to the latest schema and adds the
    default configuration items if they are missing"""
    alembic_version_table_exists = db.engine.dialect.has_table(db.session.connection(), 'alembic_version')

    if not alembic_version_table_exists:
        virtual_domains_table_exists = db.engine.dialect.has_table(db.session.connection(), 'virtual_domains')
        virtual_users_table_exists = db.engine.dialect.has_table(db.session.connection(), 'virtual_users')
        virtual_aliases_table_exists = db.engine.dialect.has_table(db.session.connection(), 'virtual_aliases')

        # If the alembic_version table doesn't exist and the virtual_* tables exist, that means the database is
        # in the default state after following the mail server guide on Linode or DigitalOcean.
        if virtual_domains_table_exists and virtual_users_table_exists and virtual_aliases_table_exists:
            # This marks the first revision as complete, which is the revision that creates the virtual_* tables
            flask_migrate.stamp(revision='bcc85aaa7896')

    flask_migrate.upgrade()
    add_default_configuration_settings()


@manager.shell
def make_shell_context():
    """Returns app, db, models to the shell"""
    return dict(app=app, db=db, models=models)


@manager.command
def clean():
    """Cleans the codebase of temporary files"""
    for root, dir_names, file_names in walk(path.abspath(path.dirname(__file__))):
        pyc_regex = compile('.+\.pyc$')
        pyo_regex = compile('.+\.pyo$')
        tilde_regex = compile('.+~$')

        for file_name in file_names:

            if pyc_regex.match(file_name) or pyo_regex.match(file_name) or tilde_regex.match(file_name) \
                    or file_name == 'postmaster.log':
                remove(path.join(root, file_name))

        for dir_name in dir_names:

            if dir_name == '__pycache__':
                rmtree(path.join(root, dir_name))


@manager.command
def generatekey():
    """Replaces the SECRET_KEY in config.py with a new random one"""
    for line in input('config.py', inplace=True):
        print(sub(r'(?<=SECRET_KEY = \')(.+)(?=\')', urandom(24).encode('hex'), line.rstrip()))


@manager.command
def setdburi(uri):
    """Replaces the BaseConfiguration SQLALCHEMY_DATABASE_URI in config.py with one supplied"""
    base_config_set = False
    for line in input('config.py', inplace=True, backup='.bak'):
        if not base_config_set and 'SQLALCHEMY_DATABASE_URI' in line:
            print(sub(r'(?<=SQLALCHEMY_DATABASE_URI = \')(.+)(?=\')', uri, line.rstrip()))
            base_config_set = True
        else:
            print(line.rstrip())


@manager.command
def setlogfile(filepath):
    """Replaces the BaseConfiguration LOG_LOCATION in config.py with one supplied"""
    base_config_set = False
    for line in input('config.py', inplace=True, backup='.bak'):
        if not base_config_set and 'LOG_LOCATION' in line:
            print(sub(r'(?<=LOG_LOCATION = \')(.+)(?=\')', filepath, line.rstrip()))
            base_config_set = True
        else:
            print(line.rstrip())


@manager.command
def unlockadmin(username):
    """Unlocks a locked out administrator"""
    clear_lockout_fields_on_user(username)


@manager.command
def resetadminpassword(username, new_password):
    """Resets an administrator's password with one supplied"""
    reset_admin_password(username, new_password)


@manager.command
def version():
    """Returns the version of PostMaster"""
    return __version__


if __name__ == "__main__":
    manager.run()
