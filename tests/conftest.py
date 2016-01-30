import pytest
from swagmail import app, db, models
app.config['WTF_CSRF_ENABLED'] = False

def initialize():
    try:
        db.session.remove()
        db.drop_all()
        db.create_all()

        min_pw_length = models.Configs().from_json({'setting': 'Minimum Password Length', 'value': '8'})
        config_login_auditing = models.Configs().from_json({'setting': 'Login Auditing', 'value': 'False'})
        config_maildb_auditing = models.Configs().from_json({'setting': 'Mail Database Auditing', 'value': 'True'})
        config_log_path = models.Configs().from_json({'setting': 'Log File', 'value': 'swagmail.log'})

        try:
            db.session.add(min_pw_length)
            db.session.add(config_login_auditing)
            db.session.add(config_maildb_auditing)
            db.session.add(config_log_path)
            db.session.commit()
        except:
            return False

        user = models.Admins().from_json({'email': 'user@swagmail.com', 'password': 'password', 'name': 'Default User'})

        try:
            db.session.add(user)
            db.session.commit()
        except:
            return False

        domain = models.VirtualDomains().from_json({'name':'swagmail.com'})
        domain2 = models.VirtualDomains().from_json({'name':'swagmail.org'})

        try:
            db.session.add(domain)
            db.session.add(domain2)
            db.session.commit()
        except:
            return False

        emailUser = models.VirtualUsers().from_json({'email': 'email@swagmail.com', 'password': 'password'})
        emailUser2 = models.VirtualUsers().from_json({'email': 'email2@swagmail.com', 'password': 'password'})
        emailUser3 = models.VirtualUsers().from_json({'email': 'email@swagmail.org', 'password': 'password'})

        try:
            db.session.add(emailUser)
            db.session.add(emailUser2)
            db.session.add(emailUser3)
            db.session.commit()
        except:
            return False

        alias = models.VirtualAliases().from_json({'domain_id': 1, 'source': 'aliasemail@swagmail.com', 'destination': 'email@swagmail.com'})
        alias2 = models.VirtualAliases().from_json({'domain_id': 1, 'source': 'aliasemail2@swagmail.com', 'destination': 'email2@swagmail.com'})
        alias3 = models.VirtualAliases().from_json({'domain_id': 1, 'source': 'aliasemail3@swagmail.com', 'destination': 'email@swagmail.org'})

        try:
            db.session.add(alias)
            db.session.add(alias2)
            db.session.add(alias3)
            db.session.commit()
        except:
            return False
        
        return True

    except Exception as e:
        print "Unexpected error: %s" % e.message
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
            username='user@swagmail.com',
            password='password'
        ),
        follow_redirects=True
    )

    return client
