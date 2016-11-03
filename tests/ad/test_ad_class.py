import functools
import ldap3
import pytest
from mock import patch, Mock
from os import path
from tests.conftest import app
import postmaster.ad


def manage_mock_ldap(f):
    """ Decorates test functions to start and stop the mocked LDAP directory
    """
    @functools.wraps(f)
    def wrapped(self, *args, **kwargs):
        # Creates the mocked LDAP instance with the directory defined in the class
        mock_server = ldap3.Server('ldaps://server.domain.local:636', get_info=ldap3.OFFLINE_AD_2012_R2)
        mock_ldap_connection = ldap3.Connection(
            mock_server, client_strategy=ldap3.MOCK_SYNC, authentication=ldap3.SIMPLE)
        ldap_entries = path.join(path.abspath(path.dirname(__file__)), 'ad_ldap_directory.json')
        # Add the mock entries
        mock_ldap_connection.strategy.entries_from_json(ldap_entries)
        # Patch ldap3.Connection so that in ad.__init__, self.ldap_connection is assigned this mocked one
        with patch('ldap3.Connection'):
            ldap3.Connection = Mock(return_value=mock_ldap_connection)
            self.ad_obj = postmaster.ad.AD()
        # Runs the decorated function
        rv = f(self, *args, **kwargs)

        # Cleans up the mock LDAP directory
        mock_ldap_connection.unbind()
        self.ad_obj = None
        return rv
    return wrapped


class TestAdFunctions:
    """ A pytest class that tests the AD class' functionality
    """
    ad_obj = None

    @manage_mock_ldap
    def test_login_pass(self):
        """ Tests the login function and expects a return value of True
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True

    @manage_mock_ldap
    def test_login_fail(self):
        """ Tests the login function with a wrong password and expects a return value of ADException
        """
        with pytest.raises(postmaster.ad.ADException) as excinfo:
            self.ad_obj.login('user', 'WrongPassword')
        assert excinfo.value.message == 'The username or password was incorrect'

    @manage_mock_ldap
    def test_parse_username_input_with_domain(self):
        """ Tests the parse_username_input function when the username input is postmaster\username
        """
        assert self.ad_obj.parse_username_input('postmaster\\testUser3') == 'postmaster\\testUser3'

    @manage_mock_ldap
    def test_parse_username_input_with_upn(self):
        """ Tests the parse_username_input function when the username input is username@postmaster.local
        """
        assert self.ad_obj.parse_username_input('testUser@postmaster.local') == 'postmaster.local\\testUser'

    @manage_mock_ldap
    def test_parse_username_input_with_no_domain(self):
        """ Tests the parse_username_input function when the username input is username
        """
        assert self.ad_obj.parse_username_input('testUser3') == 'postmaster.local\\testUser3'

    @manage_mock_ldap
    def test_parse_username_input_with_dn_and_not_ntlm(self):
        """ Tests the parse_username_input function when the username input is a distinguishedName and the
        authentication method is not ntlm
        """
        assert self.ad_obj.parse_username_input('CN=Test User,OU=PostMaster,DC=postmaster,DC=local') == \
               'CN=Test User,OU=PostMaster,DC=postmaster,DC=local'

    @manage_mock_ldap
    def test_search_with_attr(self):
        """ Test the search function with one desired attribute
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        assert self.ad_obj.search('(displayName=Test User)', ['name']) == [{
            'attributes': {'name': u'Test User'},
            'dn': 'CN=Test User,OU=PostMaster,DC=postmaster,DC=local',
            'raw_attributes': {'name': ['Test User']},
            'type': 'searchResEntry'
        }]

    @manage_mock_ldap
    def test_search_without_attr(self):
        """ Test the search function with no desired attributes
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        assert self.ad_obj.search('(displayName=Test User)') == [{
            'attributes': {},
            'dn': u'CN=Test User,OU=PostMaster,DC=postmaster,DC=local',
            'raw_attributes': {},
            'type': 'searchResEntry'
        }]

    @manage_mock_ldap
    def test_get_ldap_object(self):
        """ Test the search function with no desired attributes
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        assert self.ad_obj.get_ldap_object('Domain Users') == {
            'attributes': {},
            'dn': 'CN=Domain Users,CN=Users,DC=postmaster,DC=local',
            'raw_attributes': {},
            'type': 'searchResEntry'
        }

    @manage_mock_ldap
    def test_get_loggedin_user_loggedin(self):
        """ Tests the get_loggedin_user function with user being the distinguished name and expects the return value to
        be testUser
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        self.ad_obj.ldap_connection.user = 'postmaster\\testUser'
        assert self.ad_obj.get_loggedin_user() == 'testUser'

    @manage_mock_ldap
    def test_get_loggedin_user_loggedin_with_dn(self):
        """ Tests the get_loggedin_user function and expects the return value to be testUser
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        # For some reason, the mocked instance returns the sAMAccountName as a list
        assert self.ad_obj.get_loggedin_user() == 'testUser'

    @manage_mock_ldap
    def test_get_loggedin_user_display_name(self):
        """ Tests the get_loggedin_user_display_name function which expects the return
        value of Test User
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        assert self.ad_obj.get_loggedin_user_display_name() == 'Test User'

    @manage_mock_ldap
    def test_get_loggedin_user_display_name_when_none(self):
        """ Tests the get_loggedin_user_display_name function on a user which does not have the
        displayName attribute specified. It expects the return of the name attribute which is testUser2
        """
        assert self.ad_obj.login(
            'CN=testUser2,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        assert self.ad_obj.get_loggedin_user_display_name() == 'testUser2'

    @manage_mock_ldap
    def test_get_primary_group_dn_of_user(self):
        """ Tests the get_primary_group_dn_of_user function and tests that the primary group's
        distinguished name can be found when passing the sAMAccountName of testUser. The distinguished
        name of Domain Users is expected as the return value
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        assert self.ad_obj.get_primary_group_dn_of_user('testUser') == \
               'CN=Domain Users,CN=Users,DC=postmaster,DC=local'

    @manage_mock_ldap
    def test_get_distinguished_name(self):
        """ Tests the get_distinguished_name function and expects the return value
        of the users's distinguished name
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        assert self.ad_obj.get_distinguished_name('testUser') == \
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local'

    @manage_mock_ldap
    def test_check_nested_group_membership(self):
        """ Tests the check_nested_group_membership function and expects the return value
        of the users's distinguished name
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        responses = []
        responses.append([{'dn': u'CN=PostMaster Admins,OU=Groups,DC=postmaster,DC=local', 'attributes': {},
                          'raw_attributes': {}, 'type': 'searchResEntry'}])
        responses.append([{'dn': u'CN=Test User,OU=PostMaster,DC=postmaster,DC=local',
                          'attributes': {}, 'raw_attributes': {}, 'type': 'searchResEntry'}])
        responses.append([{'dn': u'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'attributes': {},
                           'raw_attributes': {}, 'type': 'searchResEntry'}])

        # Since ldap3's mock server doesn't support AD specific functions, we need to mock the search
        def mock_search(*args, **kwargs):
            # Set the response because that is what actually returns the results from a search
            self.ad_obj.ldap_connection.response = responses[0]
            # Remove the response just used so the next time this is called, the next response is used
            responses.pop(0)
            return True

        self.ad_obj.ldap_connection.search = mock_search
        self.ad_obj.check_nested_group_membership('PostMaster Admins', 'testUser') is True

    @manage_mock_ldap
    def test_check_group_membership_pass_memberof(self):
        """ Tests the check_group_membership function and that the user's group membership matches
        the administrative LDAP group specified in the database. A return value of True is expected
        """
        assert self.ad_obj.login(
            'CN=Test User,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        with patch('postmaster.ad.AD.check_nested_group_membership', return_value=True):
            assert self.ad_obj.check_group_membership() is True

    @manage_mock_ldap
    def test_check_group_membership_pass_primary_group(self):
        """ Tests the check_group_membership function and that the user's primaryGroupID matches
        the administrative LDAP group specified in the database. A return value of True is expected
        """
        assert self.ad_obj.login(
            'CN=testUser2,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        with patch('postmaster.ad.AD.check_nested_group_membership', return_value=False):
            assert  self.ad_obj.check_group_membership() is True

    @manage_mock_ldap
    def test_check_group_membership_fail(self):
        """ Tests the check_group_membership function and that the user is not authorized
        to use Post Master. A return value of ADException is expected
        """
        assert self.ad_obj.login(
                'CN=Test User3,OU=PostMaster,DC=postmaster,DC=local', 'P@ssW0rd') is True
        with patch('postmaster.ad.AD.check_nested_group_membership', return_value=False):
            with pytest.raises(postmaster.ad.ADException) as excinfo:
                self.ad_obj.check_group_membership()
        assert excinfo.value.message == 'The user account is not authorized to login to PostMaster'

    @manage_mock_ldap
    def test_validate_wtforms_password(self):
        """ Tests the validate_wtforms_password function by logging in with an authorized LDAP user,
        and expects the Dashboard page (view when logged in) to be returned
        """
        # Mocks the AD instantiation in validate_wtforms_password with the Mocked LDAP instance
        # created from the manage_mock_ldap decorator
        with patch('postmaster.ad.AD') as mock_ad:
            self.ad_obj.check_nested_group_membership = Mock(return_value=True)
            mock_ad.return_value = self.ad_obj
            client = app.test_client()
            rv = client.post(
                '/login',
                data=dict(
                    username='CN=Test User,OU=PostMaster,DC=postmaster,DC=local',
                    password='P@ssW0rd',
                    auth_source='postmaster.local'
                ),
                follow_redirects=True
            )

        assert '<h2 class="textHeading">Dashboard</h2>' in rv.data
