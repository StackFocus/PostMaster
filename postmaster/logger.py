"""
Author: StackFocus
File: utils.py
Purpose: logging function
"""
import json
from datetime import datetime
from os import path
from postmaster import app, models
from postmaster.errors import ValidationError


def maildb_auditing_enabled():
    """ Returns a bool based on if mail db auditing is enabled
    """
    auditing_setting = models.Configs.query.filter_by(
        setting='Mail Database Auditing').first().value
    return auditing_setting == 'True'


def login_auditing_enabled():
    """ Returns a bool based on if mail db auditing is enabled
    """
    auditing_setting = models.Configs.query.filter_by(
        setting='Login Auditing').first().value
    return auditing_setting == 'True'


def json_logger(category, admin, message):
    """ Takes a category (typically error or audit), a log message and the responsible
    user. It then appends it with an ISO 8601 UTC timestamp to a JSON formatted log file
    """
    log_path = app.config.get('LOG_LOCATION')
    if log_path and ((category == 'error') or
       (category == 'audit' and maildb_auditing_enabled()) or
       (category == 'auth' and login_auditing_enabled())):
        try:
            with open(log_path, mode='a+') as log_file:
                log_file.write("{}\n".format(json.dumps(
                    {
                        'category': category,
                        'message': message,
                        'admin': admin,
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    },
                    sort_keys=True)))
                log_file.close()
        except IOError:
            raise ValidationError('The log could not be written to "{0}". '
                                  'Verify that the path exists and is writeable.'.format(path.abspath(log_path)))
