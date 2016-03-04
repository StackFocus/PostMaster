FROM ubuntu:14.04.3
MAINTAINER Swagger.pro
ENV DEBIAN_FRONTEND noninteractive

RUN ln -snf /bin/bash /bin/sh
RUN mkdir -p /opt/postmaster/git
RUN mkdir -p /opt/postmaster/logs

COPY ./ /opt/postmaster/git

RUN chown -R www-data:www-data /opt/postmaster
RUN apt-get update
RUN apt-get install -y \
    python-dev \
    python-virtualenv \
    python-pip \
    apache2 \
    libapache2-mod-wsgi \
    libsasl2-dev \
    python-dev \
    libldap2-dev \
    libssl-dev \
    libyaml-dev \
    libpython2.7-dev \
    sqlite3 \
    libmysqlclient-dev

RUN apt-get autoremove -y
RUN apt-get clean
RUN /usr/sbin/apache2ctl stop
RUN virtualenv -p /usr/bin/python2.7 /opt/postmaster/env

WORKDIR /opt/postmaster/git

RUN /opt/postmaster/env/bin/pip install -r requirements.txt
RUN source /opt/postmaster/env/bin/activate && python manage.py clean
RUN chown -R www-data:www-data /opt/postmaster
RUN chmod +x /opt/postmaster/git/ops/docker.sh
RUN /usr/sbin/a2dissite 000-default.conf
RUN cp -f ops/apache.conf /etc/apache2/sites-available/postmaster.conf
RUN /usr/sbin/a2ensite postmaster.conf

EXPOSE 80

ENTRYPOINT /opt/postmaster/git/ops/docker.sh
