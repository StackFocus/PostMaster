from flask import request
from flask_login import login_required, current_user
from swagmail import db
from swagmail.models import VirtualUsers, VirtualAliases
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1
from utils import json_logger, maildb_auditing_enabled


@apiv1.route("/users", methods=["GET"])
@login_required
@paginate()
def get_users():
    return VirtualUsers.query


@apiv1.route("/users/<int:user_id>", methods=["GET"])
@login_required
@json_wrap
def get_user(user_id):
    return VirtualUsers.query.get_or_404(user_id)


@apiv1.route('/users', methods=['POST'])
@login_required
@json_wrap
def new_user():
    user = VirtualUsers().from_json(request.get_json(force=True))
    db.session.add(user)
    try:
        db.session.commit()
        if maildb_auditing_enabled():
            json_logger('audit', current_user.email,
                        'The user "{0}" was created successfully'.format(user.email))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error',
            'The following error occurred in new_user: {0}'.format(str(e)))
        raise GenericError('The user could not be created')
    finally:
        db.session.close()
    return {}, 201


@apiv1.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_user(user_id):
    user = VirtualUsers.query.get_or_404(user_id)

    aliases = VirtualAliases.query.filter_by(destination=user.email).all()
    if aliases:
        for alias in aliases:
            db.session.delete(alias)
    db.session.delete(user)
    try:
        db.session.commit()
        if maildb_auditing_enabled():
            json_logger(
                'audit', current_user.email,
                'The user "{0}" was deleted successfully'.format(user.email))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error',
            'The following error occurred in delete_user: {0}'.format(str(e)))
        raise GenericError('The user could not be deleted')
    finally:
        db.session.close()
    return {}, 204


@apiv1.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@json_wrap
def update_user(user_id):
    user = VirtualUsers.query.get_or_404(user_id)
    json = request.get_json(force=True)

    if 'password' in json:
        user.password = VirtualUsers().encrypt_password(json['password'])
        auditMessage = 'The user "{0}" had their password changed'.format(
            user.email)
        db.session.add(user)
    else:
        raise ValidationError('The password was not supplied in the request')
    try:
        db.session.commit()
        if maildb_auditing_enabled():
            json_logger('audit', current_user.email, auditMessage)
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error',
            'The following error occurred in update_user: {0}'.format(str(e)))
        raise GenericError('The user could not be updated')
    finally:
        db.session.close()
    return {}, 200
