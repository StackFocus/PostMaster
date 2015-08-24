## SwagMail
[![Build Status](https://travis-ci.org/thatarchguy/SwagMail.svg)](https://travis-ci.org/thatarchguy/SwagMail)![Python](https://img.shields.io/badge/python-2.7-blue.svg)![Flask](http://flask.pocoo.org/static/badges/made-with-flask-s.png)

Because managing your mailserver should be easier

### Installing
```
$ pip install -r requirements.txt
$ python app.py
```
### Tests
```
$ py.test tests/
```

### Docker!
We use docker to scale this application.
```
$ docker build .
$ docker run -p 0.0.0.0:80:8080 [image id]
```

### Screenshots
