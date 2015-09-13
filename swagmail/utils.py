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


def getAllFromTable(table):
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


def getDomain(domain):
    """ Returns a domain from VirtualDomains
    """

    queriedDomain = models.VirtualDomains.query.filter_by(name=domain).first()
    if queriedDomain:
        queriedDomainDict = queriedDomain.__dict__
        # Remove the unnecessary SQLAlchemy key
        queriedDomainDict.pop('_sa_instance_state', None)
        return queriedDomainDict


def getDomains():
    """ Returns all domains from VirtualDomains
    """

    return getAllFromTable('VirtualDomains')


def addDomain(domain):
    """ Adds a domain to VirtualDomains
    """

    if not getDomain(domain):

        try:
            db.session.add(models.VirtualDomains(domain))
            db.session.commit()
            return True
        except:
            db.session.rollback()
            raise
    else:
        raise ValidationError('The domain "%s" already exists' % domain)

    return False


def getUser(email):
    """ Returns a user from VirtualUsers
    """

    queriedUser = models.VirtualUsers.query.filter_by(email=email).first()

    if queriedUser:
        queriedUserDict = queriedUser.__dict__
        # Remove the unnecessary SQLAlchemy key
        queriedUserDict.pop('_sa_instance_state', None)
        return queriedUserDict

    return None


def getUsers():
    """ Returns all users from VirtualUsers
    """

    return getAllFromTable('VirtualUsers')


def addUser(email, password):
    """ Adds a user to VirtualUsers
    """

    if not getUser(email):

        # Checks if the domain can be extracted and if the email is at least somewhat in the right format
        if search('(?<=@).*$', email) and match('[a-z].*@.*[.].*[a-z]$', email):
            domain = search('(?<=@).*$', email).group(0)
            domainRow = getDomain(domain)

            if domainRow and 'id' in domainRow:
                salt = (sha1(urandom(16)).hexdigest())[:16]
                passwordAndSalt = sha512.encrypt(password, rounds=5000,
                                                 salt=salt, implicit_rounds=True)
                try:
                    newUser = models.VirtualUsers(domainRow['id'], passwordAndSalt, email)
                    db.session.add(newUser)
                    db.session.commit()
                    return True

                except:
                    db.session.rollback()
                    raise
            else:
                raise ValidationError('The domain "%s" is not managed by this database' % domain)
        else:
            raise ValidationError('"%s" is not a valid email address' % email)
    else:
        raise ValidationError('The user "%s" already exists' % email)

    return False


def getAlias(source):
    """ Returns alias from VirtualAliases
    """

    queriedAlias = models.VirtualAliases.query.filter_by(source=source).first()

    if queriedAlias:
        queriedAliasDict = queriedAlias.__dict__
        # Remove the unnecessary SQLAlchemy key
        queriedAliasDict.pop('_sa_instance_state', None)
        return queriedAliasDict

    return None


def getAliases():
    """ Returns all aliases from VirtualAliases
    """
    return getAllFromTable('VirtualAliases')


def addAlias(source, destination):
    """ Adds an alias to VirtualAliases
    """

    if not getAlias(source):

        sourceDomain = search('(?<=@).*$', source).group(0)
        destinationDomain = search('(?<=@).*$', destination).group(0)

        if sourceDomain == destinationDomain:

            if match('.*@.*[.].*[a-z]$', source):

                if getUser(destination):
                    domainRow = getDomain(destinationDomain)

                    if domainRow and 'id' in domainRow:
                        try:
                            alias = models.VirtualAliases(domainRow['id'], source, destination)
                            db.session.add(alias)
                            db.session.commit()
                            return True

                        except:
                            db.session.rollback()
                            raise

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
    else:
        raise ValidationError('The alias "%s" already exists' % source)

    return False
