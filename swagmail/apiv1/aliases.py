from flask import jsonify, request
from flask_login import login_required
from swagmail import db
from swagmail.models import VirtualAliases
from ..decorators import json_wrap, paginate
from ..errors import ValidationError
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
    alias = VirtualAliases().from_json(request.get_json(force=True))
    db.session.add(alias)
    db.session.commit()
    return {}, 201


@apiv1.route('/aliases/<int:alias_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_alias(alias_id):
    alias = VirtualAliases.query.get_or_404(alias_id)
    db.session.delete(alias)
    db.session.commit()
    return {}, 204


@apiv1.route('/aliases/<int:alias_id>', methods=['PUT'])
@login_required
@json_wrap
def update_alias(alias_id):
    alias = VirtualAliases.query.get_or_404(alias_id)
    json = request.get_json(force=True)

    if 'source' in json:
        if VirtualAliases().validate_source(json['source']):
            alias.source = json['source']
            db.session.commit()
    elif 'destination' in json:
        if VirtualAliases().validate_destination(json['destination']):
            alias.destination = json['destination']
            db.session.commit()
    else:
        raise ValidationError('The source or destination was not supplied in the request')

    db.session.commit()
    return {}, 200
