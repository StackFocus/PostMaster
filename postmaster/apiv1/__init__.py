"""
Author: StackFocus
File: __init__.py
Purpose: initializes apiv1
"""

from flask import Blueprint
from postmaster.errors import (
    ValidationError, GenericError, bad_request, not_found)

apiv1 = Blueprint('apiv1', __name__, url_prefix='/api/v1')

# Import the API routes
from postmaster.apiv1 import (  # noqa: F401
    domains, users, aliases, admins, configs, logs)


@apiv1.errorhandler(ValidationError)
def validation_error(e):
    """ Error handler for ValidationError exceptions
    """
    return bad_request(e.args[0])


@apiv1.errorhandler(GenericError)
def generic_error(e):
    """ Error handler for GenericError exceptions
    """
    return bad_request(e.args[0])


@apiv1.errorhandler(400)
def bad_request_error(e):
    """ Error handler for 400 requests
    """
    return bad_request('An invalid request was received')


@apiv1.errorhandler(404)
def not_found_error(e):
    """ Error handler for 404 requests
    """
    return not_found('The item was not found')
