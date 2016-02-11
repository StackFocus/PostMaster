FROM ubuntu:14.04.3
MAINTAINER Swagger.pro

ENV DEBIAN_FRONTEND noninteractive
RUN mkdir -p /opt/postmaster/git
COPY ./ /opt/postmaster/git
RUN chown -R www-data:www-data /opt/postmaster
VOLUME ["/opt/postmaster/git"]
RUN apt-get update
RUN apt-get install -y \
    python-dev \
    python-virtualenv \
    python-pip \
    apache2 \
    libapache2-mod-wsgi
RUN apt-get clean

RUN /usr/sbin/apache2ctl stop
RUN virtualenv /opt/postmaster/env
RUN . /opt/postmaster/env/bin/activate
WORKDIR /opt/postmaster/git
RUN pip install -r requirements.txt
RUN python manage.py clean && python manage.py createdb
RUN /usr/sbin/a2dissite 000-default.conf
RUN cp -f ops/apache.conf /etc/apache2/sites-available/postmaster.conf
RUN /usr/sbin/a2ensite postmaster.conf

EXPOSE 80

ENTRYPOINT /usr/sbin/apache2ctl -D FOREGROUND
