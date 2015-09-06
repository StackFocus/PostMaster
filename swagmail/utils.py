"""
Author: Swagger.pro
File: utils.py
Purpose: General helper utils
"""
from re import search, match
from os import urandom
from passlib.hash import sha512_crypt as sha512 #pylint: disable=no-name-in-module
from hashlib import sha1
from swagmail import db, models

class ValidationError(Exception):
    """ A custom exception for invalid input
    """
    pass

class MailDb(object):
    """ A class for for wrapping the SQLAlchemy models
    VirtualDomains, VirtualUsers, and Virtual Aliases
    """

    def __init__(self):
        pass


    def getAllFromTable(self, table): # pylint: disable=no-self-use
        """ Returns the entire table that is specified
        """

        # Dynamically get the model to query based on the table variable
        tableModel = getattr(models, table)

        if tableModel:
            items = tableModel.query.all()
            itemsDict = []

            for item in items:
                itemDict = []
                itemDict = item.__dict__
                # Remove the unnecessary SQLAlchemy key
                itemDict.pop('_sa_instance_state', None)
                itemsDict.append(itemDict)

            return itemsDict

        return None


    def addDomain(self, domain): # pylint: disable=no-self-use
        """ Adds a domain to VirtualDomains
        """

        db.session.add(models.VirtualDomains(domain))
        db.session.commit()

        return True


    def getDomain(self, domain): # pylint: disable=no-self-use
        """ Returns a domain from VirtualDomains
        """

        queriedDomain = models.VirtualDomains.query.filter_by(name=domain).first()
        if queriedDomain:
            queriedDomainDict = queriedDomain.__dict__
            # Remove the unnecessary SQLAlchemy key
            queriedDomainDict.pop('_sa_instance_state', None)
            return queriedDomainDict


    def getDomains(self):
        """ Returns all domains from VirtualDomains
        """

        return self.getAllFromTable('VirtualDomains')


    def addUser(self, email, password):
        """ Adds a user to VirtualUsers
        """

        domain = search('(?<=@).*$', email).group(0)
        domainRow = self.getDomain(domain)

        if domainRow and 'id' in domainRow:

            # Check to see if the email is at least somewhat in the right format
            if match('.*@.*[.].*[a-z]$', email):
                salt = (sha1(urandom(16)).hexdigest())[:16]
                passwordAndSalt = sha512.encrypt(password, rounds=5000,
                                                 salt=salt, implicit_rounds=True)

                newUser = models.VirtualUsers(domainRow['id'], passwordAndSalt, email)
                db.session.add(newUser)

                db.session.commit()
                return True

            else:
                raise ValidationError('"%s" is not a valid email address' % domain)
        else:
            raise ValidationError('The domain "%s" is not managed by this database' % domain)

        return False


    def getUser(self, email): # pylint: disable=no-self-use
        """ Returns a user from VirtualUsers
        """

        queriedUser = models.VirtualUsers.query.filter_by(email=email).first()

        if queriedUser:
            queriedUserDict = queriedUser.__dict__
            # Remove the unnecessary SQLAlchemy key
            queriedUserDict.pop('_sa_instance_state', None)
            return queriedUserDict

        return None


    def getUsers(self):
        """ Returns all users from VirtualUsers
        """

        return self.getAllFromTable('VirtualUsers')


    def addAlias(self, source, destination):
        """ Adds an alias to VirtualAliases
        """

        sourceDomain = search('(?<=@).*$', source).group(0)
        destinationDomain = search('(?<=@).*$', destination).group(0)

        if sourceDomain == destinationDomain:

            if match('.*@.*[.].*[a-z]$', source):

                if self.getUser(destination):
                    domainRow = self.getDomain(destinationDomain)

                    if domainRow and 'id' in domainRow:
                        alias = models.VirtualAliases(domainRow['id'], source, destination)
                        db.session.add(alias)
                        db.session.commit()
                        return True

                    else:
                        raise ValidationError \
                            ('The domain "%s" is not managed by this database' % sourceDomain)

                else:
                    raise ValidationError \
                        ('The destination "%s" is not a current email address' % destination)
            else:
                raise ValidationError('The source "%s" is not in a valid email format' % source)
        else:
            raise ValidationError('The domains from the source and destination alias do not match')

        return False


    def getAlias(self, source): # pylint: disable=no-self-use
        """ Returns alias from VirtualAliases
        """

        queriedAlias = models.VirtualAliases.query.filter_by(source=source).first()

        if queriedAlias:
            queriedAliasDict = queriedAlias.__dict__
            # Remove the unnecessary SQLAlchemy key
            queriedAliasDict.pop('_sa_instance_state', None)
            return queriedAliasDict

        return None


    def getAliases(self):
        """ Returns all aliases from VirtualAliases
        """
        return self.getAllFromTable('VirtualAliases')
