from flask import jsonify, request
from flask_login import login_required
from swagmail import db
from swagmail.models import VirtualDomains
from ..decorators import json_wrap, paginate
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
    domain = VirtualDomains().from_json(request.json)
    db.session.add(domain)
    db.session.commit()
    return {}, 201


@apiv1.route('/domains/<int:domain_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_domain(domain_id):
    domain = VirtualDomains.query.get_or_404(domain_id)
    db.session.delete(domain)
    db.session.commit()
    return {}, 204
