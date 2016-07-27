import functools
import pytest
from json import load
from mockldap import MockLdap
from mock import patch
from datetime import datetime, timedelta
from postmaster import app, bcrypt
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

    def test_get_wtforms_errors(self):
        """ Tests the get_wtforms_errors function by posting to /login with missing parameters.
        This also tests the new_line_to_break Jinja2 filter. The expected return value is an
        error stating that both the username and password was not provided with a <br> in between
        """
        client = app.test_client()
        rv = client.post(
            '/login',
            data=dict(
                auth_source='PostMaster User'
            ),
            follow_redirects=True
        )
        assert 'The username was not provided<br>The password was not provided' in rv.data

    def test_account_lockout_from_ui(self):
        """ Tests that the user gets an account lockout message after 5 failed attempts.
        """
        client = app.test_client()

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

        assert 'The user is currently locked out. Please try logging in again later.' in rv.data


def manage_mock_ldap(f):
    """ Decorates test functions to start and stop the mocked LDAP directory
    """
    @functools.wraps(f)
    def wrapped(self, *args, **kwargs):
        # Creates the MockLdap instance with our directory defined in the class
        self.mock_ldap_obj = MockLdap(self.directory)
        self.mock_ldap_obj.start()
        # Instantiate the AD object
        self.ad_obj = AD()
        # Get the LDAP string from the database
        ldap_server = models.Configs().query.filter_by(setting='AD Server LDAP String').first().value
        # Replace ldap_connection with the connection to the mock LDAP directory
        self.ad_obj.ldap_connection = self.mock_ldap_obj[ldap_server]

        # Runs the decorated function
        rv = f(self, *args, **kwargs)

        # Cleans up the mock LDAP directory
        self.mock_ldap_obj.stop()
        self.ad_obj = None
        return rv
    return wrapped


def mocked_nested_group_membership_query():
    """ Returns mocked output of the member:1.2.840.113556.1.4.1941 LDAP query
    """
    return [('CN=Some Group,OU=Groups,DC=postmaster,DC=local',
             {'distinguishedName': ['CN=Some Group,OU=Groups,DC=postmaster,DC=local']}),
            ('CN=PostMaster Admins,OU=Groups,DC=postmaster,DC=local',
             {'distinguishedName': ['CN=ADReset Users,OU=Groups,DC=postmaster,DC=local']}),
            (None,
             ['ldaps://ForestDnsZones.postmaster.local/DC=ForestDnsZones,DC=postmaster,DC=local']),
            (None,
             ['ldaps://DomainDnsZones.postmaster.local/DC=DomainDnsZones,DC=postmaster,DC=local']),
            (None, ['ldaps://postmaster.local/CN=Configuration,DC=postmaster,DC=local'])]



def mocked_get_nested_group_members():
    """ Returns mocked output of the get_nested_group_members function
    """
    return ['cn=testuser,cn=users,dc=postmaster,dc=local',
            'cn=someuser,cn=users,dc=postmaster,dc=local']


class TestAdFunctions:
    """ A pytest class that tests the AD class' functionality
    """
    domain = (
        'DC=postmaster,DC=local', {
            'objectClass': ['top', 'domain', 'domainDNS'],
            'name': ['postmaster'],
            'distinguishedName': ['DC=postmaster,DC=local'],
            # Using a hex SID because the AD class converts the returned hex SID to a string format
            'objectSid':
                ['\x01\x04\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00=\x12\xb7KE\xa7\x8d\xe2wZ\xff\xb3']
        }
    )

    domain_users_group = (
        'CN=Domain Users,CN=Users,DC=postmaster,DC=local', {
            'objectClass': ['top', 'group'],
            'distinguishedName': ['CN=Domain Users,CN=Users,DC=postmaster,DC=local'],
            'sAMAccountName': ['Domain Users'],
            # Using a human readable SID because AD can be queried for hex or human readable
            # the AD class will be querying by the human readable format
            'objectSid': ['S-1-5-21-1270288957-3800934213-3019856503-513']
        }
    )

    post_master_admins_group = (
        'CN=PostMaster Admins,OU=Groups,DC=postmaster,DC=local', {
            'objectClass': ['top', 'group'],
            'distinguishedName': ['CN=PostMaster Admins,OU=Groups,DC=postmaster,DC=local'],
            'sAMAccountName': ['PostMaster Admins'],
            # Using a human readable SID because AD can be queried for hex or human readable
            # the AD class will be querying by the human readable format
            'objectSid': ['S-1-5-21-1270288957-3800934213-3019856503-1105']
        }
    )

    # A test user that is authorized to use PostMaster based on group membership
    test_user = (
        'CN=testUser,CN=Users,DC=postmaster,DC=local', {
            'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
            'distinguishedName': ['CN=testUser,CN=Users,DC=postmaster,DC=local'],
            'sAMAccountName': ['testUser'],
            'userPrincipalName': ['testUser@PostMaster.local'],
            'displayName': ['Test User'],
            'name': ['testUser'],
            # Although AD uses unicodePwd for its password, MockLDAP only supports userPassword for logins
            'userPassword': ['P@ssW0rd'],
            'primaryGroupID': ['513'],
            'memberOf': ['CN=Some Group,OU=Groups,DC=postmaster,DC=local',
                         'CN=PostMaster Admins,OU=Groups,DC=postmaster,DC=local']
        }
    )

    # A test user that is authorized to use PostMaster based on the primaryGroupID being PostMaster Admins
    test_user2 = (
        'CN=testUser2,CN=Users,DC=postmaster,DC=local', {
            'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
            'distinguishedName': ['CN=testUser,CN=Users,DC=postmaster,DC=local'],
            'sAMAccountName': ['testUser2'],
            'userPrincipalName': ['testUser2@PostMaster.local'],
            'name': ['testUser2'],
            # Although AD uses unicodePwd for its password, MockLDAP only supports userPassword for logins
            'userPassword': ['P@ssW0rd'],
            'primaryGroupID': ['1105'],
            'memberOf': ['CN=Some Group,OU=Groups,DC=postmaster,DC=local',
                         'CN=Some Group2,OU=Groups,DC=postmaster,DC=local']
        }
    )

    # A test user that is not authorized to use PostMaster based on group membership
    test_user3 = (
        'CN=testUser3,CN=Users,DC=postmaster,DC=local', {
            'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
            'distinguishedName': ['CN=testUser3,CN=Users,DC=postmaster,DC=local'],
            'sAMAccountName': ['testUser3'],
            'userPrincipalName': ['testUser3@PostMaster.local'],
            'displayName': ['Test User3'],
            'name': ['testUser3'],
            # Although AD uses unicodePwd for its password, MockLDAP only supports userPassword for logins
            'userPassword': ['P@ssW0rd'],
            'primaryGroupID': ['513'],
            'memberOf': ['CN=Some Group,OU=Groups,DC=postmaster,DC=local',
                         'CN=Some Group2,OU=Groups,DC=postmaster,DC=local']
        }
    )

    directory = dict([domain, domain_users_group, post_master_admins_group, test_user, test_user2, test_user3])
    mock_ldap_obj = None
    ad_obj = None

    @manage_mock_ldap
    def test_login_pass(self):
        """ Tests the login function and expects a return value of True
        """
        assert self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                 self.test_user[1]['userPassword'][0]) is True

    @manage_mock_ldap
    def test_login_fail(self):
        """ Tests the login function with a wrong password and expects a return value of ADException
        """
        with pytest.raises(ADException) as excinfo:
            self.ad_obj.login(self.test_user[1]['distinguishedName'][0], 'WrongPassword')
        assert excinfo.value.message == 'The username or password was incorrect'

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @manage_mock_ldap
    def test_get_loggedin_user(self, mock_whoami_s):
        """ Tests the get_loggedin_user function and expects the return value to be testUser
        """
        assert self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                 self.test_user[1]['userPassword'][0]) is True
        assert self.ad_obj.get_loggedin_user() == 'testUser'

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @manage_mock_ldap
    def test_get_loggedin_user_display_name(self, mock_whoami_s):
        """ Tests the get_loggedin_user_display_name function which expects the return
        value of Test User
        """
        assert self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                 self.test_user[1]['userPassword'][0]) is True
        assert self.ad_obj.get_loggedin_user_display_name() == 'Test User'

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser2')
    @manage_mock_ldap
    def test_get_loggedin_user_display_name_when_none(self, mock_whoami_s):
        """ Tests the get_loggedin_user_display_name function on a user which does not have the
        displayName attribute specified. It expects the return of the name attribute which is testUser2
        """
        assert self.ad_obj.login(self.test_user2[1]['distinguishedName'][0],
                                 self.test_user2[1]['userPassword'][0]) == True
        assert self.ad_obj.get_loggedin_user_display_name() == 'testUser2'

    @manage_mock_ldap
    def test_sid2str(self):
        """ Tests the sid2str function by passing a SID in hex and expects a return
        value of a human readable SID
        """
        sid = self.ad_obj.sid2str(
            '\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00=\x12\xb7KE\xa7\x8d\xe2wZ\xff\xb3Q\x04\x00\x00')
        assert sid == 'S-1-5-21-1270288957-3800934213-3019856503-1105'

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @manage_mock_ldap
    def test_get_primary_group_dn_of_user(self, mock_whoami_s):
        """ Tests the get_primary_group_dn_of_user function and tests that the primary group's
        distinguished name can be found when passing the sAMAccountName of testUser. The distinguished
        name of Domain Users is expected as the return value
        """
        assert self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                 self.test_user[1]['userPassword'][0]) is True
        # MockLdap returns the result as lowercase which is why upper is needed for the assert
        assert self.ad_obj.get_primary_group_dn_of_user(self.test_user[1]['sAMAccountName'][0]).upper() == \
            'CN=Domain Users,CN=Users,DC=postmaster,DC=local'.upper()

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @manage_mock_ldap
    def test_get_distinguished_name(self, mock_whoami_s):
        """ Tests the get_distinguished_name function and expects the return value
        of the users's distinguished name
        """
        assert self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                 self.test_user[1]['userPassword'][0]) is True
        # MockLdap returns the result as lowercase which is why upper is needed for the assert
        assert self.ad_obj.get_distinguished_name(self.test_user[1]['sAMAccountName'][0]).upper() == \
               self.test_user[1]['distinguishedName'][0].upper()

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    # This must be patched as this type of query is only valid in Active Directory
    @patch('mockldap.ldapobject.LDAPObject.search_s', return_value=mocked_nested_group_membership_query())
    @manage_mock_ldap
    def test_check_nested_group_membership(self, mock_nested_group_membership_query, mock_whoami_s):
        """ Tests the check_nested_group_membership function and expects the return value
        of the users's distinguished name
        """
        assert self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                 self.test_user[1]['userPassword'][0]) is True
        assert self.ad_obj.check_nested_group_membership(self.post_master_admins_group[1]['distinguishedName'][0],
                                                         self.test_user[1]['distinguishedName'][0]) is True

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    # Simpler to patch this in order to reduce the overall amount of patches
    @patch('postmaster.utils.AD.check_nested_group_membership', return_value=True)
    @manage_mock_ldap
    def test_check_group_membership_pass_memberof(self, mock_check_nested_group_membership, mock_whoami_s):
        """ Tests the check_group_membership function and that the user's group membership matches
        the administrative LDAP group specified in the database. A return value of True is expected
        """
        assert self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                 self.test_user[1]['userPassword'][0]) is True
        assert self.ad_obj.check_group_membership() is True

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser2')
    # Simpler to patch this in order to reduce the overall amount of patches
    @patch('postmaster.utils.AD.check_nested_group_membership', return_value=False)
    @manage_mock_ldap
    def test_check_group_membership_pass_primary_group(self, mock_check_nested_group_membership, mock_whoami_s):
        """ Tests the check_group_membership function and that the user's primaryGroupID matches
        the administrative LDAP group specified in the database. A return value of True is expected
        """
        assert self.ad_obj.login(self.test_user2[1]['distinguishedName'][0],
                                 self.test_user2[1]['userPassword'][0]) is True
        assert self.ad_obj.check_group_membership() is True

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser3')
    # Simpler to patch this in order to reduce the overall amount of patches
    @patch('postmaster.utils.AD.check_nested_group_membership', return_value=False)
    @manage_mock_ldap
    def test_check_group_membership_fail(self, mock_check_nested_group_membership, mock_whoami_s):
        """ Tests the check_group_membership function and that the user is not authorized
        to use Post Master. A return value of ADException is expected
        """
        assert self.ad_obj.login(self.test_user3[1]['distinguishedName'][0],
                                 self.test_user3[1]['userPassword'][0]) is True
        with pytest.raises(ADException) as excinfo:
            self.ad_obj.check_group_membership()
        assert excinfo.value.message == 'The user account is not authorized to login to PostMaster'

    def test_add_ldap_user_to_db(self):
        """ Tests the add_ldap_user_to_db function and expects that the database
        entry exist after the function is ran
        """
        add_ldap_user_to_db('someUser', 'Some User')
        if models.Admins.query.filter_by(username='someUser', name='Some User', source='ldap').first():
            assert True
        else:
            assert False, 'The LDAP user was not found in the database.'

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @patch('postmaster.utils.AD')
    # Simpler to patch this in order to reduce the overall amount of patches
    @patch('postmaster.utils.AD.check_nested_group_membership', return_value=True)
    @manage_mock_ldap
    def test_validate_wtforms_password(self, mock_check_nested_group_membership, mock_ad, mock_whoami_s):
        """ Tests the validate_wtforms_password function by logging in with an authorized LDAP user,
        and expects the Dashboard page (view when logged in) to be returned
        """
        # Mocks the AD instantiation in validate_wtforms_password with the Mocked LDAP instance
        # created from the manage_mock_ldap decorator
        mock_ad.return_value = self.ad_obj

        client = app.test_client()
        rv = client.post(
            '/login',
            data=dict(
                username='CN=testUser,CN=Users,DC=postmaster,DC=local',
                password='P@ssW0rd',
                auth_source='postmaster.local'
            ),
            follow_redirects=True
        )

        assert '<h2 class="textHeading">Dashboard</h2>' in rv.data
