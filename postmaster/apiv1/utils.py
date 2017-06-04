"""
Author: StackFocus
File: utils.py
Purpose: General helper utils
"""

import os
from re import match
from mmap import mmap
from json import loads
from postmaster.errors import ValidationError
from postmaster import app
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


def is_config_update_valid(setting, value, valid_value_regex):
    """ A helper function for the update_config function on the
    /configs/<int:config_id> PATCH route. A bool is returned based on if the
    user's input is valid.
    """
    if match(valid_value_regex, value):
        if setting == 'Login Auditing' or setting == 'Mail Database Auditing':
            log_path = app.config.get('LOG_LOCATION')
            if not log_path or not is_file_writeable(log_path):
                error_msg = ('The log could not be written to "{0}". Verify '
                             'that the path exists and is writeable.'
                             .format(os.path.abspath(log_path)))
                raise ValidationError(error_msg)

        elif setting == 'Enable LDAP Authentication':
            ldap_string = Configs.query.filter_by(
                setting='AD Server LDAP String').first().value
            ad_domain = Configs.query.filter_by(
                setting='AD Domain').first().value
            ad_group = Configs.query.filter_by(
                setting='AD PostMaster Group').first().value

            if not (ldap_string and ad_domain and ad_group):
                error_msg = ('The LDAP settings must be configured before '
                             'LDAP authentication is enabled')
                raise ValidationError(error_msg)

        elif setting == 'AD Server LDAP String' or setting == 'AD Domain' \
                or setting == 'AD PostMaster Group':
            ldap_enabled = Configs.query.filter_by(
                setting='Enable LDAP Authentication').first().value

            if ldap_enabled == 'True' and not value:
                error_msg = ('LDAP authentication must be disabled when '
                             'deleting LDAP configuration items')
                raise ValidationError(error_msg)

        return True
    else:
        if setting in ['Minimum Password Length', 'Account Lockout Threshold']:
            error_msg = ('An invalid value was supplied. The value must be '
                         'between 0-25.')
            raise ValidationError(error_msg)
        elif setting in ['Account Lockout Duration in Minutes',
                         'Reset Account Lockout Counter in Minutes']:
            error_msg = ('An invalid value was supplied. The value must be '
                         'between 1-99.')
            raise ValidationError(error_msg)
        elif setting == 'LDAP Authentication Method':
            error_msg = ('An invalid value was supplied. The value must be '
                         'either "NTLM" or "SIMPLE"')
            raise ValidationError(error_msg)

        raise ValidationError('An invalid setting value was supplied')


def get_logs_dict(numLines=50, reverseOrder=False):
    """
    Returns the JSON formatted log file as a dict
    """
    logPath = app.config.get('LOG_LOCATION')
    if logPath and os.path.exists(logPath):
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

        return {'items': [loads(log.decode('utf-8')) for log in logs], }
    else:
        raise ValidationError('The log file could not be found')
