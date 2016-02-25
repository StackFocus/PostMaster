"""
Author: Swagger.pro
File: utils.py
Purpose: General helper utils
"""

import os
from mmap import mmap
from json import dumps, loads
from datetime import datetime
from ..errors import ValidationError
from postmaster.models import Configs


def is_file_writeable(file):
    """ Returns a bool based on if a file is writable or not
    """
    if os.path.isfile(file):
        return os.access(file, os.W_OK)
    else:
        absolute_path = os.path.abspath(file)
        dir_of_file = os.path.dirname(absolute_path)
        return os.access(dir_of_file, os.W_OK)


def maildb_auditing_enabled():
    """ Returns a bool based on if mail db auditing is enabled
    """
    auditingSetting = Configs.query.filter_by(
        setting='Mail Database Auditing').first().value
    return auditingSetting == 'True'


def login_auditing_enabled():
    """ Returns a bool based on if mail db auditing is enabled
    """
    auditingSetting = Configs.query.filter_by(
        setting='Login Auditing').first().value
    return auditingSetting == 'True'


def json_logger(category, admin, message):
    """
    Takes a category (typically error or audit), a log message and the responsible
    user. It then appends it with an ISO 8601 UTC timestamp to a JSON formatted log file
    """
    logPath = Configs.query.filter_by(setting='Log File').first().value
    if (category == 'audit' and maildb_auditing_enabled()) or\
       (category == 'auth' and login_auditing_enabled()) or\
       (category == 'error'):
        try:
            with open(logPath, mode='a+') as logFile:
                logFile.write("{}\n".format(dumps(
                    {
                        'category': category,
                        'message': message,
                        'admin': admin,
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    },
                    sort_keys=True)))
                logFile.close()
        except IOError:
            raise ValidationError(
                'The log could not be written to  "{0}". \
                Verify that the path exists and is writeable.'.format(
                    os.getcwd().replace('\\', '/') + '/' + logPath))


def get_logs_dict(numLines=50, reverseOrder=False):
    """
    Returns the JSON formatted log file as a dict
    """
    logPath = Configs.query.filter_by(setting='Log File').first().value
    if os.path.exists(logPath):
        logFile = open(logPath, mode='r+')

        try:
            mmapHandler = mmap(logFile.fileno(), 0)
        except ValueError as e:
            if str(e) == 'cannot mmap an empty file':
                # If the file is empty, return empty JSON
                return {'items': [], }
            else:
                raise ValidationError(
                    'There was an error opening "{0}"'.format(
                        os.getcwd().replace('\\', '/') + '/' + logPath))

        newLineCount = 0
        # Assigns currentChar to the last character of the file
        currentChar = mmapHandler.size() - 1

        # If the file ends in a new line, add 1 more line to process
        # for mmapHandler[currentChar:].splitlines() later on
        if mmapHandler[currentChar] == '\n':
            numLines += 1

        # While the number of lines iterated is less than numLines
        # and the beginning of the file hasn't been reached
        while newLineCount < numLines and currentChar > 0:
            # If a new line character is found, this means
            # the current line has ended
            if mmapHandler[currentChar] == '\n':
                newLineCount += 1
            # Subtract from the charcter count to read the previous character
            currentChar -= 1

        # If the beginning of the file hasn't been reached,
        # strip the preceeding new line character
        if currentChar > 0:
            currentChar += 2

        # Create the list
        logs = mmapHandler[currentChar:].splitlines()

        # Close the log file
        mmapHandler.close()
        logFile.close()

        if reverseOrder:
            logs = list(reversed(logs))

        return {'items': [loads(log) for log in logs], }
    else:
        raise ValidationError(
            '"{0}" could not be found.'.format(
                os.getcwd().replace('\\', '/') + '/' + logPath))
