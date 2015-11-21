import pytest
from swagmail import app, db, models
app.config['WTF_CSRF_ENABLED'] = False

def initialize():
    try:
        db.session.remove()
        db.drop_all()

        db.create_all()
        user = models.Admins(
            'Default User', 'user@swagmail.com',
            '$2a$12$OihMM.ogbjvUZWPLqHfBZOU4vzSjbhvypuGxef4NjbERRc839LKOy',
            False,
            True
        )

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

        try:
            db.session.add(emailUser)
            db.session.add(emailUser2)
            db.session.commit()
        except:
            return False

        alias = models.VirtualAliases().from_json({'domain_id': 1, 'source': 'aliasemail@swagmail.com', 'destination': 'email@swagmail.com'})
        alias2 = models.VirtualAliases().from_json({'domain_id': 1, 'source': 'aliasemail2@swagmail.com', 'destination': 'email2@swagmail.com'})

        try:
            db.session.add(alias)
            db.session.add(alias2)
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
