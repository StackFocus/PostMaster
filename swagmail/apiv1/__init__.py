from flask import Blueprint
from ..errors import ValidationError, bad_request, not_found


apiv1 = Blueprint('apiv1', __name__, url_prefix='/api/v1')


@apiv1.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@apiv1.errorhandler(400)
def bad_request_error(e):
    return bad_request('invalid request')


@apiv1.errorhandler(404)
def not_found_error(e):
    return not_found('item not found')


from . import domains, users, aliases
