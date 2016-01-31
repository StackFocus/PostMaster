#!/bin/bash
### Prerequisites ###
apt-get update
apt-get -y install python-pip python-dev apache2 libapache2-mod-wsgi

chown -R www-data:www-data /opt/swagmail
find /opt/swagmail -type d -exec chmod 770 {} +
find /opt/swagmail -type f -exec chmod 760 {} +

### Setup the Python environment ###
cd /opt/swagmail/git
pip install -r requirements.txt
python manage.py clean
python manage.py createdb

cat << EOT > /etc/apache2/sites-available/swagmail.conf
<VirtualHost *:80>
    WSGIDaemonProcess swagmail user=www-data group=www-data threads=5
    WSGIScriptAlias / /opt/swagmail/git/swagmail.wsgi

    <Directory /opt/swagmail/git/>
        WSGIProcessGroup swagmail
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Require all granted
    </Directory>
</VirtualHost>
EOT

a2enmod wsgi
a2dissite 000-default.conf
a2ensite swagmail.conf
service apache2 restart
