### Getting Started

- Create the config file with `cp config.default.py config.py`

- Create a Python virtualenv with `mkvirtualenv postmaster`

- Install the dependencies with `pip install -r requirements.txt -r test-requirements.txt`

- Create the SQLite database with `POSTMASTER_DEV=TRUE python manage.py upgradedb`

- Run the development server with `POSTMASTER_DEV=TRUE python manage.py runserver --reload`

- Access PostMaster at [http://127.0.0.1:5000](http://127.0.0.1:5000) via your web browser

- Login using the username "admin" and the password "PostMaster"


#### Run the Unit Tests

On the Vagrant guest, activate the virtualenv (see above) and run the following in "/opt/postmaster/git":
```
$ py.test tests
```
