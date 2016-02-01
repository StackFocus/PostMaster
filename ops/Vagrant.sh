#!/bin/bash
apt-get update
apt-get -y install python-pip python-dev apache2 libapache2-mod-wsgi

chown -R www-data:www-data /opt/swagmail
find /opt/swagmail -type d -exec chmod 770 {} +
find /opt/swagmail -type f -exec chmod 760 {} +

pip install virtualenv
virtualenv /opt/swagmail/env
source /opt/swagmail/env/bin/activate

cd /opt/swagmail/git
pip install -r requirements.txt
python manage.py clean
python manage.py createdb

deactivate

cp /opt/swagmail/git/ops/apache.conf /etc/apache2/sites-available/swagmail.conf
chmod 644 /etc/apache2/sites-available/swagmail.conf

a2enmod wsgi
a2dissite 000-default.conf
a2ensite swagmail.conf
service apache2 restart
