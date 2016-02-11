## PostMaster
[![Build Status](https://travis-ci.org/thatarchguy/SwagMail.svg)](https://travis-ci.org/thatarchguy/SwagMail)![Python](https://img.shields.io/badge/python-2.7-blue.svg)![Flask](http://flask.pocoo.org/static/badges/made-with-flask-s.png)

Because managing your mailserver should be easier

### Installing
```
$ pip install -r requirements.txt
$ python manage.py createdb
$ python manage.py runserver
```
### Tests
```
$ py.test tests/
```

### Docker!
```
$ docker build .
$ docker run -p 0.0.0.0:80:80 -d [image id]
```

### Screenshots
