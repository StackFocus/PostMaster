from swagmail import models
from swagmail.utils import *

class TestUtilsFunctions:

    def test_getDomain(self):
        """ Tests the getDomain function
        """
        result = getDomain('swagmail.com')
        assert (result['name'] == 'swagmail.com') and ('id' in result)


    def test_getDomains(self):
        """ Tests the getDomains function
        """
        result = getDomains()
        assert (result[0]['name'] == 'swagmail.com') and ('id' in result[0]) and \
            (result[1]['name'] == 'swagmail.org') and ('id' in result[1])


    def test_addDomain(self):
        """ Tests the addDomains function
        """
        result = addDomain('swagmailer.com')
        domain = models.VirtualDomains.query.filter_by(name='swagmailer.com').first()
        assert (result == True) and (domain.name == 'swagmailer.com')


    def test_getUser(self):
        """ Tests the getUser function
        """
        result = getUser('email@swagmail.com')
        assert (result['email'] == 'email@swagmail.com') and ('id' in result) and ('password' in result) and \
            (result['password'] == '$6$d1afb4750462a67c$QfGLHzTb5tn5B2uooNisQnKm3KzhMk7cmC/eKgu9TujDPsy4YAngQ5bk08jFNSuFenH2lRseeSJPArfl60bNq.')


    def test_getUsers(self):
        """ Tests the getUsers function
        """
        result = getUsers()
        assert (result[0]['email'] == 'email@swagmail.com') and ('id' in result[0]) and \
            (result[0]['password'] == '$6$d1afb4750462a67c$QfGLHzTb5tn5B2uooNisQnKm3KzhMk7cmC/eKgu9TujDPsy4YAngQ5bk08jFNSuFenH2lRseeSJPArfl60bNq.') and \
            (result[1]['email'] == 'email2@swagmail.com') and ('id' in result[1]) and \
            (result[1]['password'] == '$6$9969cb876b2432ed$HoJIK2EoFyI4YN3n5vc1pPHf6NXjGwpdmfIpvFCLNv1ZsJnsL0K50/NLUBdaEhACOnbNKQjoX2VAEJTkuR4W//')


    def test_addUser(self):
        """ Tests the addUser function
        """
        result = addUser('someuser@swagmail.com', 'P@ssw0rd')
        user = models.VirtualUsers.query.filter_by(email='someuser@swagmail.com').first()
        assert (result == True) and (user.email == 'someuser@swagmail.com') and (user.password != None) and (user.domain_id != None)


    def test_getAlias(self):
        """ Tests the getAlias function
        """
        result = getAlias('aliasemail@swagmail.com')
        assert (result['source'] == 'aliasemail@swagmail.com') and (result['destination'] == 'email@swagmail.com')


    def test_getAliases(self):
        """ Tests the getAliases function
        """
        result = getAliases()
        assert (result[0]['source'] == 'aliasemail@swagmail.com') and (result[0]['destination'] == 'email@swagmail.com') and \
            (result[1]['source'] == 'aliasemail2@swagmail.com') and (result[1]['destination'] == 'email2@swagmail.com')


    def test_addAlias(self):
        """ Tests the addAlias function
        """
        result = addAlias('somealiasemail@swagmail.com', 'email@swagmail.com')
        alias = models.VirtualAliases.query.filter_by(source='somealiasemail@swagmail.com').first()

        assert (result == True) and (alias.source == 'somealiasemail@swagmail.com') and (alias.destination == 'email@swagmail.com')
