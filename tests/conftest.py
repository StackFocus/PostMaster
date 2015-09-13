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

        domain = models.VirtualDomains('swagmail.com')
        domain2 = models.VirtualDomains('swagmail.org')

        emailUser = models.VirtualUsers(1, '$6$d1afb4750462a67c$QfGLHzTb5tn5B2uooNisQnKm3KzhMk7cmC/eKgu9TujDPsy4YAngQ5bk08jFNSuFenH2lRseeSJPArfl60bNq.', 'email@swagmail.com')
        emailUser2 = models.VirtualUsers(1, '$6$9969cb876b2432ed$HoJIK2EoFyI4YN3n5vc1pPHf6NXjGwpdmfIpvFCLNv1ZsJnsL0K50/NLUBdaEhACOnbNKQjoX2VAEJTkuR4W//', 'email2@swagmail.com')

        alias = models.VirtualAliases(1, 'aliasemail@swagmail.com', 'email@swagmail.com')
        alias2 = models.VirtualAliases(1, 'aliasemail2@swagmail.com', 'email2@swagmail.com')

        db.session.add(user)
        db.session.add(domain)
        db.session.add(domain2)
        db.session.add(emailUser)
        db.session.add(emailUser2)
        db.session.add(alias)
        db.session.add(alias2)

        try:
            db.session.commit()
            return True
        except:
            return False

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
