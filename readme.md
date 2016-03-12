## PostMaster [![Build Status](https://travis-ci.com/thatarchguy/PostMaster.svg?token=9fn8V459Z3FjXcLyubG9&branch=master)](https://travis-ci.com/thatarchguy/PostMaster) [![Dependency Status](https://gemnasium.com/9de3737c45004fea3d1a3b7041c841f2.svg)](https://gemnasium.com/thatarchguy/PostMaster) ![Python](https://img.shields.io/badge/python-2.7-blue.svg) ![Flask](http://flask.pocoo.org/static/badges/made-with-flask-s.png)

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

### Docker
```
$ mkdir /opt/postmaster_data
$ chown root:root /opt/postmaster_data && chmod 770 /opt/postmaster_data
$ docker build -t postmaster .
$ docker run -p 0.0.0.0:80:80 -v /opt/postmaster_data:/opt/postmaster/git/db \
             -e DB_URI=mysql://user:password@mailserver.domain:3306/servermail -d postmaster
```

### Screenshots


#### Dashboard:
![Dashboard](docs/imgs/Dashboard.png?raw=true)

#### Domains:
![Domains](docs/imgs/Domains.png?raw=true)

#### Users:
![Users](docs/imgs/Users.png?raw=true)

#### Aliases:
![Aliases](docs/imgs/Aliases.png?raw=true)

#### Configurations:
![Configurations](docs/imgs/Configurations.png?raw=true)

#### Search:
![Search](docs/imgs/Search.png?raw=true)

#### Mobile:
![Mobile](docs/imgs/Mobile.png?raw=true)
