from postmaster import models
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
