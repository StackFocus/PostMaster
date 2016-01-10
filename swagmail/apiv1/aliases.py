"""
Author: Swagger.pro
File: aliases.py
Purpose: The aliases API for SwagMail which allows
an admin to create, delete, and update aliases
"""

from flask import request
from flask_login import login_required, current_user
from swagmail import db
from swagmail.models import VirtualAliases
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1
from utils import json_logger


@apiv1.route("/aliases", methods=["GET"])
@login_required
@paginate()
def get_aliases():
    """ Queries all the aliases in VirtualAliases, and returns paginated JSON
    """
    return VirtualAliases.query


@apiv1.route("/aliases/<int:alias_id>", methods=["GET"])
@login_required
@json_wrap
def get_alias(alias_id):
    """ Queries a specific alias based on ID in VirtualAliases, and returns JSON
    """
    return VirtualAliases.query.get_or_404(alias_id)


@apiv1.route('/aliases', methods=['POST'])
@login_required
@json_wrap
def new_alias():
    """ Creates a new alias in VirtualAliases, and returns HTTP 201 on success
    """
    alias = VirtualAliases().from_json(request.get_json(force=True))
    db.session.add(alias)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.email,
            'The alias "{0}" was created successfully'.format(alias.source))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.email,
            'The following error occurred in new_alias: {0}'.format(str(e)))
        raise GenericError('The alias could not be created')
    finally:
        db.session.close()
    return {}, 201


@apiv1.route('/aliases/<int:alias_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_alias(alias_id):
    """ Deletes an alias by ID in VirtualAliases, and returns HTTP 204 on success
    """
    alias = VirtualAliases.query.get_or_404(alias_id)
    db.session.delete(alias)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.email,
            'The alias "{0}" was deleted successfully'.format(alias.source))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.email,
            'The following error occurred in delete_alias: {0}'.format(str(e)))
        raise GenericError('The alias could not be deleted')
    finally:
        db.session.close()
    return {}, 204


@apiv1.route('/aliases/<int:alias_id>', methods=['PUT'])
@login_required
@json_wrap
def update_alias(alias_id):
    """ Updates an alias by ID in VirtualAliases, and returns HTTP 200 on success
    """
    alias = VirtualAliases.query.get_or_404(alias_id)
    json = request.get_json(force=True)

    if 'source' in json:
        if VirtualAliases().validate_source(json['source']):
            auditMessage = 'The alias "{0}" had their source changed to "{1}"'.format(
                alias.source, json[
                    'source'])
            alias.source = json['source']
            db.session.add(alias)
    elif 'destination' in json:
        if VirtualAliases().validate_destination(json['destination']):
            auditMessage = 'The alias "{0}" had their destination changed to "{1}"'.format(
                alias.source, json[
                    'destination'])
            alias.destination = json['destination']
            db.session.add(alias)
    else:
        raise ValidationError(
            'The source or destination was not supplied in the request')

    try:
        db.session.commit()
        json_logger('audit', current_user.email, auditMessage)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.email,
            'The following error occurred in update_alias: {0}'.format(str(e)))
        raise GenericError('The alias could not be updated')
    finally:
        db.session.close()
    return {}, 200
