#!/bin/bash
# Remove any remnants of apache if it didn't shut down properly
rm -f /var/run/apache2/apache2.pid

if [ -f /.mysql_db_created ]; then
    unset DB_URI
    exec /usr/sbin/apache2ctl -D FOREGROUND
else
    if [ -z "${DB_URI}" ]; then
        echo 'The environment variable DB_URI was not set. The application cannot run.' 1>&2
        exit 1
    fi

    source /opt/postmaster/env/bin/activate
    python manage.py setdburi "${DB_URI}"

    if python manage.py createdb; then
        python manage.py generatekey
        touch /.mysql_db_created
        unset DB_URI
        deactivate
        exec /usr/sbin/apache2ctl -D FOREGROUND
    else
        echo 'The database creation failed. Please check that the environment variable DB_URI is correct.' 1>&2
        exit 1
    fi
fi
