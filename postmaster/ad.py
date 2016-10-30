"""
Author: StackFocus
File: ad.py
Purpose: Active Directory class
"""
import ldap3
import re
from postmaster import models
from postmaster.utils import json_logger


class ADException(Exception):
    """ A custom exception for the PostMasterLDAP class
    """
    pass


class AD(object):
    """ A class that handles all the Active Directory tasks for the Flask app
    """
    ldap_connection = None
    ldap_server = None
    ldap_admin_group = None
    domain = None

    def __init__(self):
        """ The constructor that initializes the ldap_connection object
        """
        ldap_enabled = models.Configs().query.filter_by(setting='Enable LDAP Authentication').first()
        if ldap_enabled is not None and ldap_enabled.value == 'True':
            ldap_server = models.Configs().query.filter_by(setting='AD Server LDAP String').first()
            domain = models.Configs().query.filter_by(setting='AD Domain').first()
            ldap_admin_group = models.Configs().query.filter_by(setting='AD PostMaster Group').first()

            if ldap_server is not None and re.search(r'LDAP[S]?:\/\/(.*?)\:\d+', ldap_server.value, re.IGNORECASE):
                self.ldap_server = ldap_server.value

                if domain is not None and ldap_admin_group is not None:
                    self.domain = domain.value
                    self.ldap_admin_group = ldap_admin_group.value

                    ad_server = ldap3.Server(
                        ldap_server.value, allowed_referral_hosts=[('*', False)],  connect_timeout=3)
                    # Use NTLMv2 authentication so that credentials aren't set in the clear if LDAPS is not used
                    self.ldap_connection = ldap3.Connection(ad_server, auto_referrals=False, authentication=ldap3.NTLM)

                    try:
                        self.ldap_connection.open()
                    except ldap3.core.exceptions.LDAPSocketOpenError:
                        json_logger(
                            'error', 'NA',
                            'The LDAP server "{0}" could not be contacted'.format(self.ldap_server))
                        raise ADException('The LDAP server could not be contacted')
                else:
                    json_logger('error', 'NA', 'The LDAP Admin Group is not configured properly')
                    raise ADException('LDAP authentication is not properly configured')
            else:
                json_logger('error', 'NA',
                            'The LDAP server string is not configured or isn\'t properly formatted')
                raise ADException('The LDAP server could not be contacted')
        else:
            json_logger('error', 'NA', 'An LDAP authentication attempt was made but it is currently disabled')
            raise ADException('LDAP authentication is not enabled')

    def __del__(self):
        """ The destructor that disconnects from LDAP
        """
        self.ldap_connection.unbind()

    @property
    def base_dn(self):
        """ returns the base distinguished name (e.g. DC=postmaster,DC=local)
        """
        return 'DC=' + (self.domain.replace('.', ',DC='))

    def parse_username_input(self, username):
        """ Takes a username and properly formats it for authentication with Active Directory
        """
        extract_username_regex = re.compile(r'(?P<username>.+)(?:@.*)')
        # Determine if a UPN or domain was provided
        if '\\' in username:
            return username
        elif re.match(extract_username_regex, username):
            # Parse the username from the UPN
            username_search = re.search(extract_username_regex, username)
            return '{0}\\{1}'.format(self.domain, username_search.group('username'))
        else:
            return '{0}\\{1}'.format(self.domain, username)

    def login(self, username, password):
        """ Uses the supplied username and password to bind to LDAP and returns a boolean
        """
        bind_username = self.parse_username_input(username)

        self.ldap_connection.user = str(bind_username)
        self.ldap_connection.password = str(password)
        if self.ldap_connection.bind():
            return True

        json_logger(
            'auth', bind_username,
            'The administrator "{0}" entered an incorrect username or password via LDAP'.format(bind_username))
        raise ADException('The username or password was incorrect')

    def search(self, search_filter, attributes=None, search_scope=ldap3.SUBTREE):
        """ Returns LDAP objects based on the search_filter and the desired attributes
        """
        # Check if the ldap_connection is in a logged in state
        if self.ldap_connection.bound:
            if self.ldap_connection.search(
                    self.base_dn, search_filter, search_scope=search_scope, attributes=attributes):
                # Check if anything was returned
                if len(self.ldap_connection.response):
                    return self.ldap_connection.response

            json_logger(
                'error', self.get_loggedin_user(),
                'The LDAP object could not be found using the search filter "{0}"'.format(search_filter))
            raise ADException('There was an error searching the LDAP server. Please try again.')
        else:
            raise ADException('You must be logged into LDAP to search')

    def get_ldap_object(self, sam_account_name, attributes=None):
        """ Returns an LDAP object based on the sAMAccountName and the desired attributes
        """
        search_filter = '(sAMAccountName={0})'.format(sam_account_name)
        ldap_object = self.search(search_filter, attributes)[0]
        # Check if a user was returned
        if 'dn' in ldap_object:
            if attributes and 'attributes' in ldap_object:
                for attribute in attributes:
                    if attribute not in ldap_object['attributes']:
                        json_logger(
                            'error', self.get_loggedin_user(),
                            ('The object with account name "{0}" was found in LDAP, but the attribute "{1}" was'
                             ' not'.format(sam_account_name, attribute)))
                        raise ADException('There was an error searching the LDAP server. Please try again.')
            return ldap_object

        json_logger(
            'error', self.get_loggedin_user(),
            'The object with account name "{0}" could not be found in LDAP'.format(sam_account_name))
        raise ADException('There was an error searching the LDAP server. Please try again.')

    def get_loggedin_user(self):
        """ Returns the logged in username without the domain
        """
        # Check if the ldap_connection is in a logged in state
        if self.ldap_connection.bound:
            # The username is stored as DOMAIN\username, so this gets the sAMAccountName
            return re.sub(r'(^.*(?<=\\))', '', self.ldap_connection.user)

        return None

    def get_loggedin_user_display_name(self):
        """ Returns the display name or the object name if the display name is not available of the logged on user
        """
        user = self.get_ldap_object(self.get_loggedin_user(), ['displayName', 'name'])
        # If the displayName is defined, return that, otherwise, return the name which is always defined
        if user['attributes']['displayName']:
            return user['attributes']['displayName']
        else:
            return user['attributes']['name']

    def get_distinguished_name(self, sam_account_name):
        """ Gets the distinguishedName of an LDAP object based on the sAMAccountName
        """
        ldap_object = self.get_ldap_object(sam_account_name)
        return ldap_object['dn']

    def check_nested_group_membership(self, group_sam_account_name, user_sam_account_name):
        """ Checks the nested group membership of a user by supplying the sAMAccountName, and verifies if the user is a
        part of that supplied group. A list with the groups the user is a member of will be returned
        """
        group_dn = self.get_distinguished_name(group_sam_account_name)
        user_dn = self.get_distinguished_name(user_sam_account_name)
        search_filter = '(member:1.2.840.113556.1.4.1941:={0})'.format(user_dn)
        group_membership = self.search(search_filter)

        for group in group_membership:
            if 'dn' in group and group['dn'] == group_dn:
                return True

        return False

    def get_primary_group_dn_of_user(self, sam_account_name):
        """ Returns the distinguished name of the primary group of the user
        """
        user = self.get_ldap_object(sam_account_name, ['primaryGroupID'])
        primary_group_id = str(user['attributes']['primaryGroupID'])

        domain_search = self.search('(objectClass=domainDNS)', ['objectSid'], ldap3.BASE)
        if 'dn' in domain_search[0]:
            if domain_search[0] and 'attributes' in domain_search[0] and 'objectSid' in domain_search[0]['attributes']:
                domain_sid = domain_search[0]['attributes']['objectSid']
                group_search_filter = '(&(objectClass=group)(objectSid={0}-{1}))'.format(domain_sid, primary_group_id)
                group_search = self.search(group_search_filter)
                if 'dn' in group_search[0]:
                    return group_search[0]['dn']

        json_logger('error', self.get_loggedin_user(), 'The objectSid of the domain could not be found')
        raise ADException('There was an error searching the LDAP server. Please try again.')

    def check_group_membership(self):
        """ Checks the group membership of the logged on user. This will return True if the user is a member of
        the Administrator group set in the database
        """
        username = self.get_loggedin_user()
        if self.check_nested_group_membership(self.ldap_admin_group, username):
            return True

        admin_group_dn = self.get_distinguished_name(self.ldap_admin_group)
        # If the user was not a member of the group, check to see if the admin group is the primary group
        # of the user which is not included in memberOf (this is typically Domain Users)
        primary_group_dn = self.get_primary_group_dn_of_user(username)
        if admin_group_dn == primary_group_dn:
            return True

        json_logger(
            'auth', username,
            ('The LDAP user "{0}" authenticated but the login failed because they weren\'t '
                'a PostMaster administrator').format(username))
        raise ADException('The user account is not authorized to login to PostMaster')
