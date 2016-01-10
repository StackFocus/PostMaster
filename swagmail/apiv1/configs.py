"""
Author: Swagger.pro
File: configs.py
Purpose: The configs API for SwagMail which
allows an admin to update SwagMail configurations
"""

from flask import request
from flask_login import login_required, current_user
from swagmail import db
from swagmail.models import Configs
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1
from utils import json_logger

validConfigItems = {
    'Login Auditing': ('True', 'False'),
    'Mail Database Auditing': ('True', 'False')
}


@apiv1.route("/configs", methods=["GET"])
@login_required
@paginate()
def get_configs():
    """ Queries all the settings in Configs, and returns paginated JSON
    """
    return Configs.query


@apiv1.route("/configs/<int:config_id>", methods=["GET"])
@login_required
@json_wrap
def get_config(config_id):
    """ Queries a specific setting based on ID in Configs, and returns JSON
    """
    return Configs.query.get_or_404(config_id)


@apiv1.route('/configs/<int:config_id>', methods=['PUT'])
@login_required
@json_wrap
def update_config(config_id):
    """ Updates a config by ID in Configs, and returns HTTP 200 on success
    """
    auditMessage = ''
    config = Configs.query.get_or_404(config_id)
    json = request.get_json(force=True)

    if 'value' in json and json['value'] in validConfigItems[config.setting]:
        auditMessage = 'The setting "{0}" was set from "{1}" to "{2}"'.format(
            config.setting, config.value, json['value'])
        config.value = json['value']
        db.session.add(config)
    else:
        raise ValidationError('An invalid setting value was supplied')

    try:
        db.session.commit()
        json_logger('audit', current_user.email, auditMessage)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.email,
            'The following error occurred in update_config: {0}'.format(str(e)))
        raise GenericError('The configuration could not be updated')
    finally:
        db.session.close()
    return {}, 200
