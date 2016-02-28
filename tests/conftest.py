﻿import pytest
from postmaster import app, db, models

app.config.from_object('config.TestConfiguration')
SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']

def initialize():
    try:
        db.session.remove()
        db.drop_all()
        db.create_all()

        min_pw_length = models.Configs().from_json({'setting': 'Minimum Password Length', 'value': '8'})
        config_login_auditing = models.Configs().from_json({'setting': 'Login Auditing', 'value': 'False'})
        config_maildb_auditing = models.Configs().from_json({'setting': 'Mail Database Auditing', 'value': 'True'})
        config_log_path = models.Configs().from_json({'setting': 'Log File', 'value': 'postmaster.log'})
        enable_ldap_auth = models.Configs().from_json({'setting': 'Enable LDAP Authentication', 'value': 'True'})
        ldap_server = models.Configs().from_json({'setting': 'AD Server LDAP String',
                                                  'value': 'LDAPS://postmaster.local:636'})
        domain = models.Configs().from_json({'setting': 'AD Domain', 'value': 'postmaster.local'})
        ldap_admin_group = models.Configs().from_json({'setting': 'AD PostMaster Group',
                                                       'value': 'PostMaster Admins'})

        try:
            db.session.add(min_pw_length)
            db.session.add(config_login_auditing)
            db.session.add(config_maildb_auditing)
            db.session.add(config_log_path)
            db.session.add(enable_ldap_auth)
            db.session.add(ldap_server)
            db.session.add(domain)
            db.session.add(ldap_admin_group)
            db.session.commit()
        except:
            return False

        user = models.Admins().from_json({'username': 'user@postmaster.com',
                                          'password': 'password',
                                          'name': 'Default User'})

        try:
            db.session.add(user)
            db.session.commit()
        except:
            return False

        domain = models.VirtualDomains().from_json({'name': 'postmaster.com'})
        domain2 = models.VirtualDomains().from_json({'name': 'postmaster.org'})

        try:
            db.session.add(domain)
            db.session.add(domain2)
            db.session.commit()
        except:
            return False

        emailUser = models.VirtualUsers().from_json({'email': 'email@postmaster.com', 'password': 'password'})
        emailUser2 = models.VirtualUsers().from_json({'email': 'email2@postmaster.com', 'password': 'password'})
        emailUser3 = models.VirtualUsers().from_json({'email': 'email@postmaster.org', 'password': 'password'})

        try:
            db.session.add(emailUser)
            db.session.add(emailUser2)
            db.session.add(emailUser3)
            db.session.commit()
        except:
            return False

        alias = models.VirtualAliases().from_json({'domain_id': 1, 'source': 'aliasemail@postmaster.com', 'destination': 'email@postmaster.com'})
        alias2 = models.VirtualAliases().from_json({'domain_id': 1, 'source': 'aliasemail2@postmaster.com', 'destination': 'email2@postmaster.com'})
        alias3 = models.VirtualAliases().from_json({'domain_id': 1, 'source': 'aliasemail3@postmaster.com', 'destination': 'email@postmaster.org'})

        try:
            db.session.add(alias)
            db.session.add(alias2)
            db.session.add(alias3)
            db.session.commit()
        except:
            return False

        return True

    except Exception as e:
        print "Unexpected error: {0}".format(e.message)
        return False

    return False

# Create a fresh database
initialize()

@pytest.fixture(scope='module')
def loggedin_client():
    client = app.test_client()
    client.post(
        '/login',
        data=dict(
            username='user@postmaster.com',
            password='password',
            auth_source='PostMaster User'
        ),
        follow_redirects=True
    )

    return client
