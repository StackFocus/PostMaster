import pytest
from postmaster import app, db, models
from postmaster.utils import add_default_configuration_settings

app.config.from_object('config.TestConfiguration')


def initialize():
    db.session.remove()
    db.drop_all()
    db.create_all()
    add_default_configuration_settings()

    admin2 = models.Admins().from_json({
        'username': 'admin2',
        'password': 'PostMaster2',
        'name': 'Some Admin'})
    db.session.add(admin2)

    enable_ldap_auth = models.Configs.query.filter_by(
        setting='Enable LDAP Authentication').first()
    enable_ldap_auth.value = 'True'
    ldap_server = models.Configs.query.filter_by(
        setting='AD Server LDAP String').first()
    ldap_server.value = 'LDAPS://postmaster.local:636'
    domain = models.Configs.query.filter_by(setting='AD Domain').first()
    domain.value = 'postmaster.local'
    ldap_admin_group = models.Configs.query.filter_by(
        setting='AD PostMaster Group').first()
    ldap_admin_group.value = 'PostMaster Admins'
    ldap_auth_method = models.Configs.query.filter_by(
        setting='LDAP Authentication Method').first()
    # Use SIMPLE auth because ldap3 testing only allows this authentication
    # method
    ldap_auth_method.value = 'SIMPLE'
    db.session.add(enable_ldap_auth)
    db.session.add(ldap_server)
    db.session.add(domain)
    db.session.add(ldap_admin_group)
    db.session.add(ldap_auth_method)

    domain = models.VirtualDomains().from_json({'name': 'postmaster.com'})
    domain2 = models.VirtualDomains().from_json({'name': 'postmaster.org'})
    db.session.add(domain)
    db.session.add(domain2)

    email_user = models.VirtualUsers().from_json({
        'email': 'email@postmaster.com',
        'password': 'password'})
    email_user2 = models.VirtualUsers().from_json({
        'email': 'email2@postmaster.com',
        'password': 'password'})
    email_user3 = models.VirtualUsers().from_json({
        'email': 'email@postmaster.org',
        'password': 'password'})
    db.session.add(email_user)
    db.session.add(email_user2)
    db.session.add(email_user3)

    alias = models.VirtualAliases().from_json({
        'domain_id': 1,
        'source': 'aliasemail@postmaster.com',
        'destination': 'email@postmaster.com'})
    alias2 = models.VirtualAliases().from_json({
        'domain_id': 1,
        'source': 'aliasemail2@postmaster.com',
        'destination': 'email2@postmaster.com'})
    alias3 = models.VirtualAliases().from_json({
        'domain_id': 1,
        'source': 'aliasemail3@postmaster.com',
        'destination': 'email@postmaster.org'})
    db.session.add(alias)
    db.session.add(alias2)
    db.session.add(alias3)

    db.session.commit()


# Reinitialize the database before each test
@pytest.yield_fixture(autouse=True)
def run_before_tests():
    # Code that runs before each test
    initialize()
    # A test function will be run at this point
    yield


@pytest.fixture(scope='module')
def loggedin_client():
    client = app.test_client()
    client.post(
        '/login',
        data=dict(
            username='admin',
            password='PostMaster',
            auth_source='PostMaster User'
        ),
        follow_redirects=True
    )

    return client
