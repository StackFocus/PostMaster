"""
Author: Swagger.pro
File: utils.py
Purpose: General helper utils
"""
from re import search, match
from os import urandom
from passlib.hash import sha512_crypt as sha512  # pylint: disable=no-name-in-module
from hashlib import sha1
from swagmail import db, models, app
from flask import abort, jsonify, jsonify
import json


def row2dict(row):
    """ Return a dictionary from a sqlalchemy row
        We use this so we don't have to deal with
        sa_instance_state stuff
    """

    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d


def getAllFromTable(table):
    """ Returns the entire table that is specified
    """

    # Dynamically get the model to query based on the table variable
    if getattr(models, table):
        table = (getattr(models, table)).query.all()
        listItemsDict = [row2dict(row) for row in table]
        return listItemsDict

    return None


def getDomain(name):
    """ Returns a domain from VirtualDomains
    """
    queriedDomain = models.VirtualDomains.query.filter_by(name=name).first()
    if queriedDomain:
        return row2dict(queriedDomain)
    return None


def getUser(email):
    """ Returns a user from VirtualUsers
    """

    queriedUser = models.VirtualUsers.query.filter_by(email=email).first()

    if queriedUser:
        return row2dict(queriedUser)
    return None


def getAlias(source):
    """ Returns alias from VirtualAliases
    """

    queriedAlias = models.VirtualAliases.query.filter_by(source=source).first()

    if queriedAlias:
        return row2dict(queriedAlias)
    return None
