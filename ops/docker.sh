#!/bin/bash
# Remove any remnants of apache if it didn't shut down properly
rm -f /var/run/apache2/apache2.pid
# Only change the group membership so that the owner can be controlled on the Docker host when this folder is
# mounted, and grant Apache write access to the logs folder
chgrp -R www-data /opt/postmaster/logs
chmod g+rwx /opt/postmaster/logs

if [ ! -f /.mysql_db_configured ]; then

    if [ -z "${DB_URI}" ]; then
        echo 'The environment variable DB_URI was not set. The application cannot run.' 1>&2
        exit 1
    fi

    source /opt/postmaster/env/bin/activate

    if [ "${SECRET_KEY}" ]; then
        python manage.py setkey "${SECRET_KEY}"
    else
        python manage.py generatekey
    fi

    python manage.py setdburi "${DB_URI}"
    # Clean up the pyc files for the config changes to take effect
    python manage.py clean

    if ! python manage.py upgradedb; then
        echo 'The database creation failed. Please check that the environment variable DB_URI is correct.' 1>&2
        exit 1
    fi

    # Create a placeholder file to signify that the container has been configured
    touch /.mysql_db_configured
fi

unset DB_URI
unset SECRET_KEY
exec /usr/sbin/apache2ctl -D FOREGROUND
