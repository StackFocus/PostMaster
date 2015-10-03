from flask import jsonify, request
from flask_login import login_required
from swagmail import db
from swagmail.models import VirtualAliases
from ..decorators import json_wrap, paginate
from . import apiv1


@apiv1.route("/aliases", methods=["GET"])
@login_required
@paginate()
def get_aliases():
    return VirtualAliases.query


@apiv1.route("/aliases/<int:alias_id>", methods=["GET"])
@login_required
@json_wrap
def get_alias(alias_id):
    return VirtualAliases.query.get_or_404(alias_id)


@apiv1.route('/aliases', methods=['POST'])
@login_required
@json_wrap
def new_alias():
    alias = VirtualAliases().from_json(request.json)
    db.session.add(alias)
    db.session.commit()
    return {}, 201
