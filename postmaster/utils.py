"""
Author: StackFocus
File: utils.py
Purpose: General helper utils
"""
from json import dumps
from datetime import datetime
from os import path
from wtforms.validators import StopValidation as WtfStopValidation
from postmaster import app, db, models, bcrypt
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
                log_file.write("{}\n".format(dumps(
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


def add_default_configuration_settings():
    """ Adds the default configuration settings to the database if they aren't present.
    This is to be used from manage.py when creating the database.
    """
    if not models.Configs.query.filter_by(setting='Minimum Password Length').first():
        min_pwd_length = models.Configs()
        min_pwd_length.setting = 'Minimum Password Length'
        min_pwd_length.value = '8'
        min_pwd_length.regex = '^([0-9]|[1][0-9]|[2][0-5])$'
        db.session.add(min_pwd_length)

    if not models.Configs.query.filter_by(setting='Account Lockout Threshold').first():
        account_lockout_threshold = models.Configs()
        account_lockout_threshold.setting = 'Account Lockout Threshold'
        account_lockout_threshold.value = '5'
        account_lockout_threshold.regex = '^([0-9]|[1][0-9]|[2][0-5])$'
        db.session.add(account_lockout_threshold)

    if not models.Configs.query.filter_by(setting='Account Lockout Duration in Minutes').first():
        account_lockout_duration = models.Configs()
        account_lockout_duration.setting = 'Account Lockout Duration in Minutes'
        account_lockout_duration.value = '30'
        account_lockout_duration.regex = '^([1-9]|[1-9][0-9])$'
        db.session.add(account_lockout_duration)

    if not models.Configs.query.filter_by(setting='Reset Account Lockout Counter in Minutes').first():
        reset_account_lockout = models.Configs()
        reset_account_lockout.setting = 'Reset Account Lockout Counter in Minutes'
        reset_account_lockout.value = '30'
        reset_account_lockout.regex = '^([1-9]|[1-9][0-9])$'
        db.session.add(reset_account_lockout)

    if not models.Configs.query.filter_by(setting='Login Auditing').first():
        login_auditing = models.Configs()
        login_auditing.setting = 'Login Auditing'
        login_auditing.value = 'False'
        login_auditing.regex = '^(True|False)$'
        db.session.add(login_auditing)

    if not models.Configs.query.filter_by(setting='Mail Database Auditing').first():
        mail_db_auditing = models.Configs()
        mail_db_auditing.setting = 'Mail Database Auditing'
        mail_db_auditing.value = 'False'
        mail_db_auditing.regex = '^(True|False)$'
        db.session.add(mail_db_auditing)

    if not models.Configs.query.filter_by(setting='Enable LDAP Authentication').first():
        ldap_auth = models.Configs()
        ldap_auth.setting = 'Enable LDAP Authentication'
        ldap_auth.value = 'False'
        ldap_auth.regex = '^(True|False)$'
        db.session.add(ldap_auth)

    if not models.Configs.query.filter_by(setting='AD Server LDAP String').first():
        ad_server = models.Configs()
        ad_server.setting = 'AD Server LDAP String'
        ad_server.regex = '^(.*)$'
        db.session.add(ad_server)

    if not models.Configs.query.filter_by(setting='AD Domain').first():
        ad_domain = models.Configs()
        ad_domain.setting = 'AD Domain'
        ad_domain.regex = '^(.*)$'
        db.session.add(ad_domain)

    if not models.Configs.query.filter_by(setting='AD PostMaster Group').first():
        ad_group = models.Configs()
        ad_group.setting = 'AD PostMaster Group'
        ad_group.regex = '^(.*)$'
        db.session.add(ad_group)

    if not models.Admins.query.first():
        admin = models.Admins().from_json(
            {'username': 'admin', 'password': 'PostMaster', 'name': 'Default Admin'})
        db.session.add(admin)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


def increment_failed_login(username):
    """ Increments the failed_attempts value, updates the last_failed_date value, and sets the unlock_date value
    if necessary on the admin
    """
    admin = models.Admins.query.filter_by(username=username).first()
    if not admin:
        raise ValidationError('The admin does not exist in the database.')

    account_lockout_threshold = int(models.Configs.query.filter_by(setting='Account Lockout Threshold').first().value)
    reset_account_lockout_counter = int(models.Configs.query.filter_by(
        setting='Reset Account Lockout Counter in Minutes').first().value)
    account_lockout_duration = int(models.Configs.query.filter_by(
        setting='Account Lockout Duration in Minutes').first().value)

    admin.increment_failed_login(account_lockout_threshold, reset_account_lockout_counter, account_lockout_duration)

    try:
        db.session.add(admin)
        db.session.commit()

        # If the account is locked out, log an audit message
        if not admin.is_unlocked():
            audit_message = '"{0}" is now locked out and will be unlocked in {1} minute(s)'.format(
                username, account_lockout_duration)
            json_logger('audit', username, audit_message)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', username,
            'The following error occurred when incrementing the failed login attempts field on "{0}": {1}'.format(
                username, str(e)))
        ValidationError('A database error occurred. Please try again.', 'error')
    finally:
        db.session.close()


def clear_lockout_fields_on_user(username):
    """ Clears the lockout fields (failed_attempts, last_failed_date, unlock_date) on a user. This is used
    to unlock a user, or when a user logs in successfully.
    """
    admin = models.Admins.query.filter_by(username=username).first()

    if not admin:
        raise ValidationError('The admin does not exist in the database.')

    try:
        admin.clear_lockout_fields()
        db.session.add(admin)
        db.session.commit()
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', username,
            'The following error occurred when try to clear out the lockout fields: {0}'.format(str(e)))
        ValidationError('A database error occurred. Please try again.', 'error')
    finally:
        db.session.close()


def reset_admin_password(username, new_password):
    """ Resets an admin's password with one supplied
    """
    admin = models.Admins.query.filter_by(username=username).first()

    if not admin:
        raise ValidationError('The admin does not exist in the database.')

    admin.set_password(new_password)

    try:
        db.session.add(admin)
        db.session.commit()
        json_logger('audit', 'CLI', ('The administrator "{0}" had their password changed via the CLI'.format(username)))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', username,
            'The following error occurred when try to reset an admin\'s password: {0}'.format(str(e)))
        ValidationError('A database error occurred. Please try again.', 'error')
    finally:
        db.session.close()


def add_ldap_user_to_db(username, display_name):
    """ Adds an LDAP user stub in the Admins table of the database for flask_login
    """
    try:
        new_admin = models.Admins().ldap_user_from_json({
            'username': username,
            'name': display_name
        })
        db.session.add(new_admin)
        db.session.commit()
        json_logger('audit', username,
                    '"{0}" was added as an LDAP admin to the database"'.format(username))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', username,
            'The following error occurred when adding an LDAP admin: {0}'.format(str(e)))
        ValidationError('A database error occurred. Please try again.', 'error')
    finally:
        db.session.close()


def validate_wtforms_password(form, field):
        """ Validates the password from a wtforms object
        """
        # Prevent circular import on json_logger by importing here
        from postmaster.ad import AD, ADException
        username = form.username.data
        password = form.password.data
        two_factor = form.two_factor.data if form.two_factor.data else None

        try:
            if form.auth_source.data == 'PostMaster User':
                admin = models.Admins.query.filter_by(username=username, source='local').first()
                if admin:
                    if admin.is_unlocked():
                        if bcrypt.check_password_hash(admin.password, password):
                            if admin.otp_active:
                                if not admin.verify_totp(two_factor):
                                    raise WtfStopValidation('The two factor authentication code is incorrect')
                            form.admin = admin
                            return
                        else:
                            increment_failed_login(username)
                    else:
                        raise WtfStopValidation('The user is currently locked out. Please try logging in again later.')
                json_logger(
                    'auth', username,
                    'The administrator "{0}" entered an incorrect username or password'.format(
                        username))
                raise WtfStopValidation('The username or password was incorrect')
            else:
                ad_object = AD()
                if ad_object.login(username, password):
                    if ad_object.check_group_membership():
                        friendly_username = ad_object.get_loggedin_user()
                        display_name = ad_object.get_loggedin_user_display_name()
                        if not models.Admins.query.filter_by(username=friendly_username, source='ldap').first():
                            add_ldap_user_to_db(friendly_username, display_name)
                        admin = models.Admins.query.filter_by(username=friendly_username, source='ldap').first()
                        if admin.otp_active:
                            if not admin.verify_totp(two_factor):
                                raise WtfStopValidation('The two factor authentication code is incorrect')
                        form.admin = admin
        except ADException as e:
            raise WtfStopValidation(e.message)


def get_wtforms_errors(form):
    """ Returns the errors from wtforms in a single string with new lines
    """
    i = 0
    error_messages = ''
    for field, errors in form.errors.items():
        for error in errors:
            # If this isn't the first error, add a new line for the next error
            if i != 0:
                error_messages += '\n'
            # If the error is from DataRequired, make the error more user friendly
            if 'This field is required' in error:
                error_messages += 'The {0} was not provided'.format(
                    getattr(form, field).label.text.lower())
            else:
                error_messages += error
            i += 1

    return error_messages
