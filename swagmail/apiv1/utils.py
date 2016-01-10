"""
Author: Swagger.pro
File: utils.py
Purpose: General helper utils
"""

from os import getcwd
from json import dumps as dumps
from datetime import datetime
from ..errors import ValidationError
from swagmail.models import Configs


def maildb_auditing_enabled():
    """ Returns a bool based on if mail db auditing is enabled
    """
    auditingSetting = Configs.query.filter_by(setting='Mail Database Auditing').first().value
    if auditingSetting == 'True':
        return True
    else:
        return False


def login_auditing_enabled():
    """ Returns a bool based on if mail db auditing is enabled
    """
    auditingSetting = Configs.query.filter_by(setting='Login Auditing').first().value
    if auditingSetting == 'True':
        return True
    else:
        return False


def json_logger(category, admin, message):
    """
    Takes a category (typically error or audit), a log message and the responsible
    user. It then appends it with an ISO 8601 UTC timestamp to a JSON formatted log file
    """
    logPath = 'swagmail.log'
    if (category == 'audit' and maildb_auditing_enabled()) or\
       (category == 'auth' and login_auditing_enabled()) or\
       (category == 'error'):
        try:
            with open(logPath, mode='a+') as logFile:
                logFile.write("{}\n".format(dumps({
                        'category': category,
                        'message': message,
                        'admin': admin,
                        'timestamp': datetime.utcnow().isoformat() + 'Z'},
                    sort_keys=True)))
                logFile.close()
        except IOError:
            raise ValidationError(
                'The log could not be written to  "{0}". Verify that the path exists and is writeable.'.format(
                    getcwd().replace('\\', '/') + '/' + logPath))
