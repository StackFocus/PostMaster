"""
Author: StackFocus
File: utils.py
Purpose: General helper utils
"""
from wtforms.validators import StopValidation as WtfStopValidation
from postmaster.logger import json_logger
from postmaster import db, models, bcrypt
from postmaster.errors import ValidationError
from postmaster.ad import AD, ADException


def add_default_configuration_settings():
    """ Adds the default configuration settings to the database if they aren't
    present. This is to be used from manage.py when creating the database.
    """
    setting_name = 'Minimum Password Length'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        min_pwd_length = models.Configs()
        min_pwd_length.setting = setting_name
        min_pwd_length.value = '8'
        min_pwd_length.regex = '^([0-9]|[1][0-9]|[2][0-5])$'
        db.session.add(min_pwd_length)

    setting_name = 'Account Lockout Threshold'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        account_lockout_threshold = models.Configs()
        account_lockout_threshold.setting = setting_name
        account_lockout_threshold.value = '5'
        account_lockout_threshold.regex = '^([0-9]|[1][0-9]|[2][0-5])$'
        db.session.add(account_lockout_threshold)

    setting_name = 'Account Lockout Duration in Minutes'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        account_lockout_duration = models.Configs()
        account_lockout_duration.setting = setting_name
        account_lockout_duration.value = '30'
        account_lockout_duration.regex = '^([1-9]|[1-9][0-9])$'
        db.session.add(account_lockout_duration)

    setting_name = 'Reset Account Lockout Counter in Minutes'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        reset_account_lockout = models.Configs()
        reset_account_lockout.setting = setting_name
        reset_account_lockout.value = '30'
        reset_account_lockout.regex = '^([1-9]|[1-9][0-9])$'
        db.session.add(reset_account_lockout)

    setting_name = 'Login Auditing'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        login_auditing = models.Configs()
        login_auditing.setting = setting_name
        login_auditing.value = 'False'
        login_auditing.regex = '^(True|False)$'
        db.session.add(login_auditing)

    setting_name = 'Mail Database Auditing'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        mail_db_auditing = models.Configs()
        mail_db_auditing.setting = setting_name
        mail_db_auditing.value = 'False'
        mail_db_auditing.regex = '^(True|False)$'
        db.session.add(mail_db_auditing)

    setting_name = 'Enable LDAP Authentication'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        ldap_auth = models.Configs()
        ldap_auth.setting = setting_name
        ldap_auth.value = 'False'
        ldap_auth.regex = '^(True|False)$'
        db.session.add(ldap_auth)

    setting_name = 'AD Server LDAP String'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        ad_server = models.Configs()
        ad_server.setting = setting_name
        ad_server.regex = '^(.*)$'
        db.session.add(ad_server)

    setting_name = 'AD Domain'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        ad_domain = models.Configs()
        ad_domain.setting = setting_name
        ad_domain.regex = '^(.*)$'
        db.session.add(ad_domain)

    setting_name = 'AD PostMaster Group'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        ad_group = models.Configs()
        ad_group.setting = setting_name
        ad_group.regex = '^(.*)$'
        db.session.add(ad_group)

    setting_name = 'LDAP Authentication Method'
    if not models.Configs.query.filter_by(setting=setting_name).first():
        auth_method = models.Configs()
        auth_method.setting = setting_name
        auth_method.value = 'NTLM'
        auth_method.regex = '^(SIMPLE|simple|NTLM|ntlm)$'
        db.session.add(auth_method)

    if not models.Admins.query.first():
        admin = models.Admins().from_json({
            'username': 'admin',
            'password': 'PostMaster',
            'name': 'Default Admin'})
        db.session.add(admin)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


def increment_failed_login(username):
    """ Increments the failed_attempts value, updates the last_failed_date
    value, and sets the unlock_date value if necessary on the admin
    """
    admin = models.Admins.query.filter_by(username=username).first()
    if not admin:
        raise ValidationError('The admin does not exist in the database.')

    account_lockout_threshold = int(models.Configs.query.filter_by(
        setting='Account Lockout Threshold').first().value)
    reset_account_lockout_counter = int(models.Configs.query.filter_by(
        setting='Reset Account Lockout Counter in Minutes').first().value)
    account_lockout_duration = int(models.Configs.query.filter_by(
        setting='Account Lockout Duration in Minutes').first().value)

    admin.increment_failed_login(
        account_lockout_threshold, reset_account_lockout_counter,
        account_lockout_duration)

    try:
        db.session.add(admin)
        db.session.commit()

        # If the account is locked out, log an audit message
        if not admin.is_unlocked():
            audit_msg = ('"{0}" is now locked out and will be unlocked in '
                         '{1} minute(s)'.format(
                             username, account_lockout_duration))
            json_logger('audit', username, audit_msg)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        log_msg = ('The following error occurred when incrementing the failed '
                   'login attempts field on "{0}": {1}'.format(
                       username, str(e)))
        json_logger('error', username, log_msg)
        ValidationError('A database error occurred. Please try again.')
    finally:
        db.session.close()


def clear_lockout_fields_on_user(username):
    """ Clears the lockout fields (failed_attempts, last_failed_date,
    unlock_date) on a user. This is used to unlock a user, or when a user logs
    in successfully.
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
        log_msg = ('The following error occurred when try to clear out the '
                   'lockout fields: {0}'.format(str(e)))
        json_logger('error', username, log_msg)
        ValidationError('A database error occurred. Please try again.')
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
        log_msg = ('The administrator "{0}" had their password changed via '
                   'the CLI'.format(username))
        json_logger('audit', 'CLI', log_msg)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        log_msg = ('The following error occurred when trying to reset an '
                   'admin\'s password: {0}'.format(str(e)))
        json_logger('error', username, log_msg)
        ValidationError('A database error occurred. Please try again.')
    finally:
        db.session.close()


def add_ldap_user_to_db(username, display_name):
    """ Adds an LDAP user stub in the Admins table of the database for
    flask_login
    """
    try:
        new_admin = models.Admins().ldap_user_from_json({
            'username': username,
            'name': display_name
        })
        db.session.add(new_admin)
        db.session.commit()
        log_msg = ('"{0}" was added as an LDAP admin to the database"'
                   .format(username))
        json_logger('audit', username, log_msg)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        log_msg = ('The following error occurred when adding an LDAP admin: '
                   '{0}'.format(str(e)))
        json_logger('error', username, log_msg)
        ValidationError('A database error occurred. Please try again.')
    finally:
        db.session.close()


def validate_wtforms_password(form, field):
    """ Validates the password from a wtforms object
    """
    username = form.username.data
    password = form.password.data
    two_factor = form.two_factor.data if form.two_factor.data else None

    try:
        if form.auth_source.data == 'PostMaster User':
            admin = models.Admins.query.filter_by(username=username,
                                                  source='local').first()
            if admin:
                if admin.is_unlocked():
                    if bcrypt.check_password_hash(admin.password, password):
                        if admin.otp_active:
                            if not admin.verify_totp(two_factor):
                                error_msg = ('The two factor authentication '
                                             'code is incorrect')
                                raise WtfStopValidation(error_msg)
                        form.admin = admin
                        return
                    else:
                        increment_failed_login(username)
                else:
                    error_msg = ('The user is currently locked out. Please '
                                 'try logging in again later.')
                    raise WtfStopValidation(error_msg)
            log_msg = ('The administrator "{0}" entered an incorrect username '
                       'or password'.format(username))
            json_logger('auth', username, log_msg)
            raise WtfStopValidation('The username or password was incorrect')
        else:
            ad_object = AD()
            if ad_object.login(username, password) \
                    and ad_object.check_group_membership():
                friendly_username = ad_object.get_loggedin_user()
                display_name = ad_object.get_loggedin_user_display_name()
                admin = models.Admins.query.filter_by(
                    username=friendly_username, source='ldap').first()

                if not admin:
                    add_ldap_user_to_db(friendly_username, display_name)
                    admin = models.Admins.query.filter_by(
                        username=friendly_username, source='ldap').first()

                if admin.otp_active:
                    if not admin.verify_totp(two_factor):
                        raise WtfStopValidation(
                            'The two factor authentication code is incorrect')
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
            # If the error is from DataRequired, make the error more user
            # friendly
            if 'This field is required' in error:
                error_messages += 'The {0} was not provided'.format(
                    getattr(form, field).label.text.lower())
            else:
                error_messages += error
            i += 1

    return error_messages
