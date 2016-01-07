from flask import jsonify, request
from flask_login import login_required
from swagmail import db
from swagmail.models import Admins
from ..decorators import json_wrap, paginate
from ..errors import ValidationError, GenericError
from . import apiv1


@apiv1.route("/admins", methods=["GET"])
@login_required
@paginate()
def get_admins():
    return Admins.query


@apiv1.route("/admins/<int:admin_id>", methods=["GET"])
@login_required
@json_wrap
def get_admin(admin_id):
    return Admins.query.get_or_404(admin_id)
