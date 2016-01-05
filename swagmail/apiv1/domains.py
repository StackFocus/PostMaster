from flask import request
from flask_login import login_required
from swagmail import db
from swagmail.models import VirtualDomains
from ..decorators import json_wrap, paginate
from ..errors import GenericError
from . import apiv1


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
    except:
        db.session.rollback()
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
    except:
        db.session.rollback()
        raise GenericError('The domain could not be deleted')
    finally:
        db.session.close()
    return {}, 204
