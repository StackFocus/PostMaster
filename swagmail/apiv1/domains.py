from flask import request
from flask_login import login_required, current_user
from swagmail import db
from swagmail.models import VirtualDomains
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1
from utils import json_logger


@apiv1.route("/domains", methods=["GET"])
@login_required
@paginate()
def get_domains():
    return VirtualDomains.query


@apiv1.route("/domains/<int:domain_id>", methods=["GET"])
@login_required
@json_wrap
def get_domain(domain_id):
    return VirtualDomains.query.get_or_404(domain_id)


@apiv1.route('/domains', methods=['POST'])
@login_required
@json_wrap
def new_domain():
    domain = VirtualDomains().from_json(request.get_json(force=True))
    db.session.add(domain)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.email,
            'The domain "{0}" was created successfully by "{1}"'.format(
                domain.name, current_user.email))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.email,
            'The following error occurred in new_domain: {0}'.format(str(e)))
        raise GenericError('The domain could not be created')
    finally:
        db.session.close()
    return {}, 201


@apiv1.route('/domains/<int:domain_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_domain(domain_id):
    domain = VirtualDomains.query.get_or_404(domain_id)
    db.session.delete(domain)
    try:
        db.session.commit()
        json_logger(
            'audit', current_user.email,
            'The domain "{0}" was deleted successfully'.format(domain.name))
    except ValidationError as e:
        raise e
    except Exception as e:
        db.session.rollback()
        json_logger(
            'error', current_user.email,
            'The following error occurred in delete_domain: {0}'.format(str(
                e)))
        raise GenericError('The domain could not be deleted')
    finally:
        db.session.close()
    return {}, 204
