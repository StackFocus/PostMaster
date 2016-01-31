#!/bin/bash
### Prerequisites ###
apt-get update
apt-get -y install python-pip python-dev apache2 libapache2-mod-wsgi

chown -R www-data:www-data /var/www
find /var/www -type d -exec chmod 770 {} +
find /var/www -type f -exec chmod 760 {} +

### Setup the Python environment ###
cd /var/www/SwagMail
pip install -r requirements.txt
python manage.py clean
python manage.py createdb

cat << 'EOT' > /etc/apache2/sites-available/SwagMail.conf
<VirtualHost *:80>
    WSGIDaemonProcess swagmail user=www-data group=www-data threads=5
    WSGIScriptAlias / /var/www/SwagMail/swagmail.wsgi

    <Directory /var/www/SwagMail/>
        WSGIProcessGroup swagmail
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
EOT

a2enmod wsgi
a2dissite 000-default.conf
a2ensite SwagMail.conf
service apache2 restart
