"""
Author: Swagger.pro
File: views.py
Purpose: routes for the app
"""

from flask import render_template
from swagmail import app


@app.route('/', methods=['GET'])
def index():
    """ Function to return index page
    """

    return render_template('index.html')
