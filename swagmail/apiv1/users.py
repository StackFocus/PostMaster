from flask import jsonify, request
from flask_login import login_required
from swagmail import db
from swagmail.models import VirtualUsers
from ..decorators import json_wrap, paginate
from . import apiv1


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
    user = VirtualUsers().from_json(request.json)
    db.session.add(user)
    db.session.commit()
    return {}, 201


@apiv1.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@json_wrap
def delete_user(user_id):
    user = VirtualUsers.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return {}, 204
