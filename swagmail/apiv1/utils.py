"""
Author: Swagger.pro
File: utils.py
Purpose: General helper utils
"""
from os import path, getcwd
from json import dumps as dumps
from datetime import datetime
from ..errors import ValidationError

def json_logger(category, message):
    """
    Takes a category (typically error or audit) and a log message and
    appends it with an ISO 8601 UTC timestamp to a JSON formatted log file
    """
    logPath = 'swagmail.log'

    try:
        with open(logPath, mode='a+') as logFile:
            logFile.write("{}\n".format(dumps({
                    'category': category,
                    'message': message,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }, sort_keys=True)))
            logFile.close()
    except IOError:
        raise ValidationError(
            'The log could not be written to  "%s". Verify that the path exists and is writeable.'
            % (getcwd().replace('\\','/') + '/' + logPath))
