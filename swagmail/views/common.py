"""
Author: Swagger.pro
File: views.py
Purpose: routes for the app
"""

from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from swagmail.utils import getAllFromTable
from swagmail import app, forms, models, login_manager, bcrypt

common = Blueprint('common', __name__)


@login_manager.user_loader
def user_loader(user_id):
    """ Function to return user for login
    """
    if models.Admins.query.filter_by(id=user_id).first() is not None:
        return models.Admins.query.filter_by(id=user_id).first()
    else:
        return None


@login_manager.unauthorized_handler
def unauthorized_callback():
    """ Function to redirect after logging in when prompted for login
    """
    return redirect('/login?next=' + request.path)


@app.route('/', methods=['GET'])
@login_required
def index():
    """ Function to return index page
    """

    return render_template('index.html', authenticated=(current_user).is_authenticated())


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This is the login route and processing of information
    """
    loginForm = forms.LoginForm()

    if current_user.is_authenticated():
        return redirect(url_for('index'))
    else:
        if request.method == 'GET':
            return render_template('login.html',
                                   title='SwagMail Management Login',
                                   loginForm=loginForm)

        elif loginForm.validate_on_submit():

            if models.Admins.query.filter_by(email=loginForm.username.data).first() is not None:
                user = models.Admins.query.filter_by(
                    email=loginForm.username.data).first()

                if user and (bcrypt.check_password_hash(user.password, loginForm.password.data)):
                    login_user(user, remember=False)
                    return redirect(request.args.get('next') or url_for('index'))

            flash('The username or password was incorrect', 'error')
            return redirect(url_for('login'))
        else:
            flash('All fields in the login form are required', 'error')
            return redirect(url_for('login'))


@app.route('/logout', methods=["GET"])
def logout():
    """
    Logs current user out
    """
    if current_user.is_authenticated():
        logout_user()
        flash('Successfully logged out', 'success')

    return redirect(url_for('login'))


@app.route('/domains', methods=["GET"])
@login_required
def domains():
    """
    Manages domains in the database
    """

    return render_template('domains.html', authenticated=(current_user).is_authenticated())


@app.route('/users', methods=["GET"])
@login_required
def users():
    """
    Manages users/email accounts in the database
    """

    return render_template('users.html', authenticated=(current_user).is_authenticated())


@app.route('/aliases', methods=["GET"])
@login_required
def aliases():
    """
    Manages aliases in the database
    """

    return render_template('aliases.html', authenticated=(current_user).is_authenticated())

