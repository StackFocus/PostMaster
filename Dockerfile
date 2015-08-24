FROM ubuntu:latest
MAINTAINER Swagger.pro

RUN mkdir -p /opt/swagmail/git && mkdir /opt/swagmail/logs
COPY ./ /opt/swagmail/git
VOLUME ["/opt/swagmail/git"]
RUN apt-get update && apt-get install -y \
    python-dev \
    python-virtualenv \
    python-pip \
    supervisor

RUN virtualenv /opt/swagmail/env

RUN . /opt/swagmail/env/bin/activate && pip install -r /opt/swagmail/git/requirements.txt

#Probably some supervisor stuff eventually to run some wsgi to run the flask program

EXPOSE 80

CMD /usr/bin/supervisord -c /opt/swagmail/git/supervisord.conf   
