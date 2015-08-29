"""
Author: Swagger.pro
File: views.py
Purpose: routes for the app
"""

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from swagmail import app, db, forms, models, login_manager, bcrypt


@login_manager.user_loader
def user_loader(user_id):
    if models.Admins.query.filter_by(id=user_id).count() == 1:
        return models.Admins.query.filter_by(id=user_id).first()
    else:
        return None


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@app.route('/', methods=['GET'])
@login_required
def index():
    """ Function to return index page
    """

    return render_template('index.html')


@app.route('/login', methods=['Get', 'POST'])
def login():
    loginForm = forms.LoginForm()

    if (current_user).is_authenticated():
        return redirect(url_for('index'))
    else:
        if request.method == 'GET':
            return render_template('login.html', title='Flask Reminders Login', loginForm=loginForm)

        elif loginForm.validate_on_submit():

            if (models.Admins.query.filter_by(email=loginForm.username.data).count()) == 1:
                user = models.Admins.query.filter_by(
                    email=loginForm.username.data).first()

                if (bcrypt.check_password_hash(user.password, loginForm.password.data)):
                    user.authenticated = True
                    db.session.commit()
                    login_user(user, remember=False)
                    flash('Login successful', 'success')
                    return redirect(request.args.get('next') or url_for('index'))

            flash('Login is incorrect', 'error')
            return redirect(url_for('login'))
        else:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    user = current_user
    print(user.name)
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash('Logout successful', 'success')
    return redirect(url_for('login'))
