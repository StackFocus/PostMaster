"""
Author: StackFocus
File: logs.py
Purpose: The logs API for PostMaster which allows
an admin to query the log file
"""

from flask import request, jsonify
from flask_login import login_required
from . import apiv1
from utils import get_logs_dict


@apiv1.route("/logs", methods=["GET"])
@login_required
def get_logs():
    """ Queries the log file and returns the logs
    in JSON format
    """

    numLines = request.args.get('lines', 50, type=int)
    reverseOrder = request.args.get('reverse', 0, type=int)

    return jsonify(get_logs_dict(numLines, bool(reverseOrder)))
