﻿from swagmail import models
from swagmail.utils import *

class TestUtilsFunctions:

    def test_getDomain(self):
        """ Tests the getDomain function
        """
        result = getDomain('swagmail.com')
        assert (result['name'] == 'swagmail.com') and ('id' in result)


    def test_getUser(self):
        """ Tests the getUser function
        """
        result = getUser('email@swagmail.com')
        assert (result['email'] == 'email@swagmail.com') and ('id' in result) and ('password' in result) and \
            (result['password'] == '$6$d1afb4750462a67c$QfGLHzTb5tn5B2uooNisQnKm3KzhMk7cmC/eKgu9TujDPsy4YAngQ5bk08jFNSuFenH2lRseeSJPArfl60bNq.')


    def test_getAlias(self):
        """ Tests the getAlias function
        """
        result = getAlias('aliasemail@swagmail.com')
        assert (result['source'] == 'aliasemail@swagmail.com') and (result['destination'] == 'email@swagmail.com')
