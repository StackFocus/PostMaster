import functools
from mockldap import MockLdap
from mock import patch
from postmaster import app
from postmaster.utils import *
from postmaster.apiv1.utils import *


class TestUtilsFunctions:

    def test_getDomain(self):
        result = getDomain('postmaster.com')
        assert (result['name'] == 'postmaster.com') and ('id' in result)

    def test_getUser(self):
        result = getUser('email@postmaster.com')
        assert (result['email'] == 'email@postmaster.com') and (
            'id' in result) and ('password' in result)

    def test_getAlias(self):
        result = getAlias('aliasemail@postmaster.com')
        assert (result['source'] == 'aliasemail@postmaster.com') and (
            result['destination'] == 'email@postmaster.com')

    def test_maildb_auditing_enabled(self):
        result = maildb_auditing_enabled()
        assert isinstance(result, bool)

    def test_login_auditing_enabled(self):
        result = login_auditing_enabled()
        assert isinstance(result, bool)

    def test_get_logs_dict(self):
        result = get_logs_dict()
        assert isinstance(result, dict)
        assert 'items' in result

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


def mocked_nested_group_members_query():
    """ Returns mocked output of the memberOf:1.2.840.113556.1.4.1941 LDAP query
    """
    return [('cn=testuser,cn=users,dc=postmaster,dc=local', {}),
            ('cn=someuser,cn=users,dc=postmaster,dc=local', {}),
            (None, ['ldaps://ForestDnsZones.postmaster.local/DC=ForestDnsZones,DC=postmaster,DC=local']),
            (None, ['ldaps://DomainDnsZones.postmaster.local/DC=DomainDnsZones,DC=postmaster,DC=local']),
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
        result = self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                   self.test_user[1]['userPassword'][0])
        assert result is True

    @manage_mock_ldap
    def test_login_fail(self):
        """ Tests the login function with a wrong password and expects a return value of ADException
        """
        try:
            self.ad_obj.login(self.test_user[1]['distinguishedName'][0], 'WrongPassword')
            assert False, 'The login function did not throw the expected exception'
        except ADException as e:
            assert e.message == 'The username or password was incorrect'

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @manage_mock_ldap
    def test_get_loggedin_user(self, mock_whoami_s):
        """ Tests the get_loggedin_user function and expects the return value to be testUser
        """
        login_result = self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                         self.test_user[1]['userPassword'][0])
        assert login_result is True
        loggedin_user_result = self.ad_obj.get_loggedin_user()
        assert loggedin_user_result == 'testUser'

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @manage_mock_ldap
    def test_get_loggedin_user_display_name(self, mock_whoami_s):
        """ Tests the get_loggedin_user_display_name function which expects the return
        value of Test User
        """
        login_result = self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                         self.test_user[1]['userPassword'][0])
        assert login_result is True
        loggedin_user_display_name_result = self.ad_obj.get_loggedin_user_display_name()
        assert loggedin_user_display_name_result == 'Test User'

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser2')
    @manage_mock_ldap
    def test_get_loggedin_user_display_name_when_none(self, mock_whoami_s):
        """ Tests the get_loggedin_user_display_name function on a user which does not have the
        displayName attribute specified. It expects the return of the name attribute which is testUser2
        """
        login_result = self.ad_obj.login(self.test_user2[1]['distinguishedName'][0],
                                         self.test_user2[1]['userPassword'][0])
        assert login_result is True
        loggedin_user_display_name_result = self.ad_obj.get_loggedin_user_display_name()
        assert loggedin_user_display_name_result == 'testUser2'

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
        login_result = self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                         self.test_user[1]['userPassword'][0])
        assert login_result is True
        domain_users_primary_group_dn = self.ad_obj.get_primary_group_dn_of_user(
            self.test_user[1]['sAMAccountName'][0])
        # MockLdap returns the result as lowercase which is why upper is needed for the assert
        assert domain_users_primary_group_dn.upper() == 'CN=Domain Users,CN=Users,DC=postmaster,DC=local'.upper()

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @manage_mock_ldap
    def test_get_distinguished_name(self, mock_whoami_s):
        """ Tests the get_distinguished_name function and expects the return value
        of the users's distinguished name
        """
        login_result = self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                         self.test_user[1]['userPassword'][0])
        assert login_result is True
        distinguished_name = self.ad_obj.get_distinguished_name(self.test_user[1]['sAMAccountName'][0])
        # MockLdap returns the result as lowercase which is why upper is needed for the assert
        assert distinguished_name.upper() == self.test_user[1]['distinguishedName'][0].upper()

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @patch('mockldap.ldapobject.LDAPObject.search_s', return_value=mocked_nested_group_members_query())
    @manage_mock_ldap
    def test_get_nested_group_members(self, mock_nested_group_members_query, mock_whoami_s):
        """ Tests the get_nested_group_members function and expects the return value
        of the users's distinguished name
        """
        login_result = self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                         self.test_user[1]['userPassword'][0])
        assert login_result is True
        nested_groups = self.ad_obj.get_nested_group_members(self.post_master_admins_group[1]['distinguishedName'][0])
        assert nested_groups == mocked_get_nested_group_members()

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser')
    @patch('postmaster.utils.AD.get_nested_group_members', return_value=mocked_get_nested_group_members())
    @manage_mock_ldap
    def test_check_group_membership_pass_memberof(self, mock_get_nested_group_members, mock_whoami_s):
        """ Tests the check_group_membership function and that the user's group membership matches
        the administrative LDAP group specified in the database. A return value of True is expected
        """
        login_result = self.ad_obj.login(self.test_user[1]['distinguishedName'][0],
                                         self.test_user[1]['userPassword'][0])
        assert login_result is True
        group_membership_result = self.ad_obj.check_group_membership()
        assert group_membership_result is True

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser2')
    @patch('postmaster.utils.AD.get_nested_group_members', return_value=mocked_get_nested_group_members())
    @manage_mock_ldap
    def test_check_group_membership_pass_primary_group(self, mock_get_nested_group_members, mock_whoami_s):
        """ Tests the check_group_membership function and that the user's primaryGroupID matches
        the administrative LDAP group specified in the database. A return value of True is expected
        """
        login_result = self.ad_obj.login(self.test_user2[1]['distinguishedName'][0],
                                         self.test_user2[1]['userPassword'][0])
        assert login_result is True
        group_membership_result = self.ad_obj.check_group_membership()
        assert group_membership_result is True

    # Mocks the actual value returned from AD versus another LDAP directory
    @patch('mockldap.ldapobject.LDAPObject.whoami_s', return_value='POSTMASTER\\testUser3')
    @patch('postmaster.utils.AD.get_nested_group_members', return_value=mocked_get_nested_group_members())
    @manage_mock_ldap
    def test_check_group_membership_fail(self, mock_get_nested_group_members, mock_whoami_s):
        """ Tests the check_group_membership function and that the user is not authorized
        to use Post Master. A return value of ADException is expected
        """
        login_result = self.ad_obj.login(self.test_user3[1]['distinguishedName'][0],
                                         self.test_user3[1]['userPassword'][0])
        assert login_result is True
        try:
            self.ad_obj.check_group_membership()
            assert False, 'The check_group_membership function did not throw the expected exception'
        except ADException as e:
            assert e.message == 'The user account is not authorized to login to PostMaster'

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
    @patch('postmaster.utils.AD.get_nested_group_members', return_value=mocked_get_nested_group_members())
    @manage_mock_ldap
    def test_validate_wtforms_password(self, mock_get_nested_group_members, mock_ad, mock_whoami_s):
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
