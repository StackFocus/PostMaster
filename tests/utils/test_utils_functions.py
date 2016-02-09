from swagmail import models
from swagmail.utils import *
from swagmail.apiv1.utils import *


class TestUtilsFunctions:

    def test_getDomain(self):
        result = getDomain('swagmail.com')
        assert (result['name'] == 'swagmail.com') and ('id' in result)

    def test_getUser(self):
        result = getUser('email@swagmail.com')
        assert (result['email'] == 'email@swagmail.com') and (
            'id' in result) and ('password' in result)

    def test_getAlias(self):
        result = getAlias('aliasemail@swagmail.com')
        assert (result['source'] == 'aliasemail@swagmail.com') and (
            result['destination'] == 'email@swagmail.com')

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
