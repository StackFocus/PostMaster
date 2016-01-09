"""
Author: Swagger.pro
File: utils.py
Purpose: General helper utils
"""
from os import getcwd
from json import dumps as dumps
from datetime import datetime
from ..errors import ValidationError


def json_logger(category, user, message):
    """
    Takes a category (typically error or audit), a log message and the responsible
    user. It then appends it with an ISO 8601 UTC timestamp to a JSON formatted log file
    """
    logPath = 'swagmail.log'

    try:
        with open(logPath, mode='a+') as logFile:
            logFile.write("{}\n".format(dumps(
                {
                    'category': category,
                    'message': message,
                    'user': user,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                },
                sort_keys=True)))
            logFile.close()
    except IOError:
        raise ValidationError(
            'The log could not be written to  "{0}". Verify that the path exists and is writeable.'.format(
                getcwd().replace('\\', '/') + '/' + logPath))
