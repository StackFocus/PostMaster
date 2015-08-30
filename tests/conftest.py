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

        db.session.add(user)
        if db.session.commit():
            return True

    except:
        print "Unexpected error: ", sys.exc_info()[0]
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
