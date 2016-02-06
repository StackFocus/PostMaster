FROM ubuntu:14.04.3
MAINTAINER Swagger.pro

ENV DEBIAN_FRONTEND noninteractive
RUN mkdir -p /opt/swagmail/git
COPY ./ /opt/swagmail/git
RUN chown -R www-data:www-data /opt/swagmail
VOLUME ["/opt/swagmail/git"]
RUN apt-get update
RUN apt-get install -y \
    python-dev \
    python-virtualenv \
    python-pip \
    apache2 \
    libapache2-mod-wsgi
RUN apt-get clean

RUN /usr/sbin/apache2ctl stop
RUN virtualenv /opt/swagmail/env
RUN . /opt/swagmail/env/bin/activate
WORKDIR /opt/swagmail/git
RUN pip install -r requirements.txt
RUN python manage.py clean && python manage.py createdb
RUN /usr/sbin/a2dissite 000-default.conf
RUN cp -f ops/apache.conf /etc/apache2/sites-available/swagmail.conf
RUN /usr/sbin/a2ensite swagmail.conf

EXPOSE 80

ENTRYPOINT /usr/sbin/apache2ctl -D FOREGROUND
