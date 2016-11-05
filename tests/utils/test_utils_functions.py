from json import load
from mock import patch
from datetime import timedelta
from postmaster.logger import *
import tests.conftest
from postmaster.utils import *
from postmaster.apiv1.utils import *


def generate_test_admin():
    test_admin = models.Admins().from_json({
        'username': 'test_admin',
        'password': 'S0meG00dP@ss',
        'name': 'Test Admin'
    })
    return test_admin

class TestUtilsFunctions:

    def test_maildb_auditing_enabled(self):
        result = maildb_auditing_enabled()
        assert isinstance(result, bool)

    def test_login_auditing_enabled(self):
        result = login_auditing_enabled()
        assert isinstance(result, bool)

    def test_get_logs_dict(self, tmpdir):
        # Staging a fake log file
        log_file = tmpdir.join('postmaster.log')
        log_file.write('{"admin": "admin", "category": "audit", "message": "The alias \\"rawr@postmaster.com\\" was created successfully", "timestamp": "2016-07-01T00:41:06.330000Z"}\n'
                       '{"admin": "admin", "category": "audit", "message": "The alias \\"rawr2@postmaster.com\\" was created successfully", "timestamp": "2016-07-01T00:42:06.330000Z"}\n')
        app.config['LOG_LOCATION'] = str(log_file)
        result = get_logs_dict()
        # Clean up the temp directory created by the test
        tmpdir.remove()
        assert isinstance(result, dict)
        assert 'items' in result

    def test_json_logger(self, tmpdir):
        log_file = tmpdir.join('postmaster.log')
        app.config['LOG_LOCATION'] = str(log_file)
        json_logger('error', 'admin', 'This is a test error message')
        log_contents = load(log_file)
        # Clean up the temp directory created by the test
        tmpdir.remove()
        assert log_contents['admin'] == 'admin'
        assert log_contents['message'] == 'This is a test error message'
        assert log_contents['timestamp'] is not None

    @patch('os.access', return_value=True)
    def test_is_file_writeable_existing_file(self, mock_access):
        """ Tests the is_file_writeable function when a file exists and is writable.
        A return value of True is expected
        """
        assert is_file_writeable('manage.py') is True

    @patch('os.access', return_value=True)
    def test_is_file_writeable_nonexisting_file(self, mock_access):
        """ Tests the is_file_writeable function when a file does not exist but the path is writable.
        A return value of True is expected
        """
        assert is_file_writeable('S0meNonExistenFil3.SomeExtension') is True

    @patch('os.access', return_value=False)
    def test_is_file_writeable_existing_file_fail(self, mock_access):
        """ Tests the is_file_writeable function when a file exists and is not writable.
        A return value of False is expected
        """
        assert is_file_writeable('manage.py') is False

    def test_is_file_writeable_nonexisting_file_fail(self):
        """ Tests the is_file_writeable function when a file does not exist and the path is not writable.
        A return value of True is expected
        """
        assert is_file_writeable('S0meDir/S0meNonExistentFil3.SomeExtension') is False

    def test_is_unlocked_false(self):
        test_admin = generate_test_admin()
        test_admin.unlock_date = datetime.utcnow() + timedelta(minutes=30)
        db.session.add(test_admin)
        db.session.commit()

        assert test_admin.is_unlocked() is False

    def test_is_unlocked_true(self):
        test_admin = generate_test_admin()
        test_admin.unlock_date = datetime.utcnow() - timedelta(minutes=30)
        db.session.add(test_admin)
        db.session.commit()

        assert test_admin.is_unlocked() is True

    def test_is_unlocked_true_field_is_none(self):
        test_admin = generate_test_admin()
        db.session.add(test_admin)
        db.session.commit()

        assert test_admin.is_unlocked() is True

    def test_increment_failed_login_new_user(self):
        test_admin = generate_test_admin()
        test_admin_username = test_admin.username
        db.session.add(test_admin)
        db.session.commit()
        increment_failed_login(test_admin_username)
        new_test_admin = models.Admins.query.filter_by(username=test_admin_username).first()
        assert new_test_admin.failed_attempts == 1
        assert new_test_admin.unlock_date is None
        one_min_ago = datetime.utcnow() - timedelta(minutes=1)
        assert new_test_admin.last_failed_date > one_min_ago

    def test_increment_failed_login_prev_failures(self):
        test_admin = generate_test_admin()
        test_admin_username = test_admin.username
        test_admin.last_failed_date = datetime.utcnow()
        test_admin.failed_attempts = 2
        db.session.add(test_admin)
        db.session.commit()
        increment_failed_login(test_admin_username)
        new_test_admin = models.Admins.query.filter_by(username=test_admin_username).first()
        assert new_test_admin.failed_attempts == 3
        assert new_test_admin.unlock_date is None
        one_min_ago = datetime.utcnow() - timedelta(minutes=1)
        assert new_test_admin.last_failed_date > one_min_ago

    def test_increment_failed_login_lock(self):
        account_lockout_threshold = int(
            models.Configs.query.filter_by(setting='Account Lockout Threshold').first().value)
        account_lockout_duration = int(
            models.Configs.query.filter_by(setting='Account Lockout Duration in Minutes').first().value)
        account_lockout_minus_one_min = datetime.utcnow() + timedelta(minutes=(account_lockout_duration - 1))
        one_min_ago = datetime.utcnow() - timedelta(minutes=1)

        test_admin = generate_test_admin()
        test_admin_username = test_admin.username
        test_admin.failed_attempts = account_lockout_threshold - 1
        test_admin.last_failed_date = datetime.utcnow() - timedelta(minutes=5)
        db.session.add(test_admin)
        db.session.commit()
        increment_failed_login(test_admin_username)
        new_test_admin = models.Admins.query.filter_by(username=test_admin_username).first()

        assert new_test_admin.unlock_date > account_lockout_minus_one_min
        assert new_test_admin.failed_attempts == 5
        assert new_test_admin.last_failed_date > one_min_ago

    def test_increment_failed_login_time_elapsed(self):
        account_lockout_threshold = int(
            models.Configs.query.filter_by(setting='Account Lockout Threshold').first().value)
        reset_account_lockout_counter = int(models.Configs.query.filter_by(
            setting='Reset Account Lockout Counter in Minutes').first().value)
        one_min_ago = datetime.utcnow() - timedelta(minutes=1)

        test_admin = generate_test_admin()
        test_admin_username = test_admin.username
        test_admin.failed_attempts = account_lockout_threshold - 1
        test_admin.last_failed_date = datetime.utcnow() - timedelta(minutes=(reset_account_lockout_counter + 1))
        db.session.add(test_admin)
        db.session.commit()
        increment_failed_login(test_admin_username)
        new_test_admin = models.Admins.query.filter_by(username=test_admin_username).first()

        assert new_test_admin.unlock_date is None
        assert new_test_admin.failed_attempts == 1
        assert new_test_admin.last_failed_date > one_min_ago

    def test_increment_failed_login_user_lockout_disabled(self):
        account_lockout_threshold = models.Configs.query.filter_by(setting='Account Lockout Threshold').first()
        account_lockout_threshold.value = '0'
        db.session.add(account_lockout_threshold)
        test_admin = generate_test_admin()
        test_admin_username = test_admin.username
        test_admin.failed_attempts = 999
        db.session.add(test_admin)
        db.session.commit()
        increment_failed_login(test_admin_username)
        new_test_admin = models.Admins.query.filter_by(username=test_admin_username).first()
        assert new_test_admin.failed_attempts == 1000
        assert new_test_admin.unlock_date is None
        one_min_ago = datetime.utcnow() - timedelta(minutes=1)
        assert new_test_admin.last_failed_date > one_min_ago

    def test_clear_lockout_fields_on_user(self):
        test_admin = generate_test_admin()
        test_admin_username = test_admin.username
        test_admin.failed_attempts = 1
        test_admin.last_failed_date = datetime.utcnow()
        test_admin.unlock_date = datetime.utcnow() + timedelta(minutes=30)
        db.session.add(test_admin)
        db.session.commit()
        clear_lockout_fields_on_user(test_admin_username)
        new_test_admin = models.Admins.query.filter_by(username=test_admin_username).first()
        assert new_test_admin.failed_attempts == 0
        assert new_test_admin.unlock_date is None
        assert new_test_admin.last_failed_date is None

    def test_reset_admin_password(self):
        test_admin = generate_test_admin()
        db.session.add(test_admin)
        db.session.commit()
        reset_admin_password('test_admin', 'SomeNewPassword')
        new_test_admin = models.Admins.query.filter_by(username='test_admin').first()
        assert bcrypt.check_password_hash(new_test_admin.password, 'SomeNewPassword') is True

    def test_add_ldap_user_to_db(self):
        """ Tests the add_ldap_user_to_db function and expects that the database
        entry exist after the function is ran
        """
        add_ldap_user_to_db('someUser', 'Some User')
        if models.Admins.query.filter_by(username='someUser', name='Some User', source='ldap').first():
            assert True
        else:
            assert False, 'The LDAP user was not found in the database.'

    def test_get_wtforms_errors(self):
        """ Tests the get_wtforms_errors function by posting to /login with missing parameters.
        This also tests the new_line_to_break Jinja2 filter. The expected return value is an
        error stating that both the username and password was not provided with a <br> in between
        """
        client = tests.conftest.app.test_client()
        rv = client.post(
            '/login',
            data=dict(
                auth_source='PostMaster User'
            ),
            follow_redirects=True
        )
        assert 'The username was not provided<br>The password was not provided' in rv.data.decode('utf-8') or \
               'The password was not provided<br>The username was not provided' in rv.data.decode('utf-8')

    def test_account_lockout_from_ui(self):
        """ Tests that the user gets an account lockout message after 5 failed attempts.
        """
        client = tests.conftest.app.test_client()

        for i in range(6):
            rv = client.post(
                '/login',
                data=dict(
                    username='admin',
                    password='BadPassword',
                    auth_source='PostMaster User'
                ),
                follow_redirects=True
            )

        assert 'The user is currently locked out. Please try logging in again later.' in rv.data.decode('utf-8')
