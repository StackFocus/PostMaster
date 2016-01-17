"""
Author: Swagger.pro
File: logs.py
Purpose: The logs API for SwagMail which allows
an admin to query the log file
"""

from flask import request, jsonify
from flask_login import login_required
from json import loads, dumps
from . import apiv1
from utils import getLogs

@apiv1.route("/logs", methods=["GET"])
@login_required
def get_logs():
    """ Queries the log file and returns the logs
    in JSON format
    """

    numLines = request.args.get('lines', 50, type=int)
    reverseOrder = request.args.get('reverse', 0, type=int)
    if reverseOrder == 1:
        return jsonify(getLogs(numLines, True))
    else:
        return jsonify(getLogs(numLines, False))
