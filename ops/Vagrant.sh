#!/bin/bash

usage() {
cat << EOF
Usage: $0
    This script will install PostMaster using Apache or nginx
Options:
    -a : Install using Apache
    -n : Install using Nginx
    -p : Preserves the existing database

examples:
$0 -a
$0 -ap
$0 -n
$0 -np
EOF
}

INSTALL_APACHE=false
INSTALL_NGINX=false
PRESERVE=false

while getopts ":anp" opt; do
    case $opt in
        a)
            if [ $INSTALL_NGINX = false ]
            then
                INSTALL_APACHE=true
            else
                >&2 echo 'You must select either apache or nginx, not both'
                usage
                exit 1
            fi
            ;;
        n)
            if [ $INSTALL_APACHE = false ]
            then
                $INSTALL_NGINX=true
                >&2 echo 'nginx is currently not supported'
                usage
                exit 1
            else
                >&2 echo 'You must select either apache or nginx, not both'
                usage
                exit 1
            fi
            ;;
        p)
            PRESERVE=true
            ;;
        \?)
            >&2 echo "Invalid option: -$optarg"
            usage
            exit 1
            ;;
    esac
done

if [ $INSTALL_APACHE = false ] && [ $INSTALL_NGINX = false ]
then
    >&2 echo 'You must either select -a to install Apache or -n to install with nginx'
    usage
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo 'Updating the aptitude repository...'
apt-get -y update > /dev/null

packages=('python' 'python-pip' 'python-dev')
if [ INSTALL_APACHE ]
then
    packages+=('apache2' 'libapache2-mod-wsgi')
fi

for package in "${packages[@]}"
do
    if dpkg --get-selections | grep -q "^$package[[:space:]]*install$" >/dev/null
    then
        echo "Skipping the installation of $package"
    else
        echo "Installing $package..."
        apt-get install -y $package > /dev/null
    fi
done

echo 'Checking the python version...'
if [ $(python -V 2>&1 | grep -c "2.7") -eq 0 ]
then
    >&2 echo "Please ensure that python 2.7 is installed and is the default python"
    exit 1
fi

echo 'Creating the /opt/postmaster/logs directory'
mkdir /opt/postmaster/logs
chown www-data:www-data /opt/postmaster/logs

if ! [ -d '/opt/postmaster/env' ]
then
    echo 'Installing the virtual environment...'
    pip install virtualenv > /dev/null
    virtualenv /opt/postmaster/env > /dev/null
    source /opt/postmaster/env/bin/activate
else
    >&2 echo '/opt/postmaster/env already exists. Please make sure it is removed before rerunning the script'
    exit 1
fi

cd /opt/postmaster/git
echo 'Installing the Python packages required in the virtualenv...'
pip install -r requirements.txt > /dev/null

if [ $PRESERVE = false ]
then
    python manage.py clean
    python manage.py createdb
else
    echo 'Preserving the existing database'
fi

deactivate

if [ $INSTALL_APACHE = true ]
then
    if [ $(apachectl -M | grep -c 'wsgi_module') == 0 ]
    then
        echo 'Enabling the wsgi module for Apache...'
        a2enmod -q wsgi > /dev/null
    fi

    if [ $(apachectl -S | grep -c "000-default.conf") != 0 ]
    then
        echo 'Disabling 000-default.conf...'
        a2dissite 000-default.conf > /dev/null
    fi

    echo 'Copying and enabling the standard PostMaster Apache configuration...'
    cp -f /opt/postmaster/git/ops/apache.conf /etc/apache2/sites-available/postmaster.conf
    chmod 644 /etc/apache2/sites-available/postmaster.conf
    a2ensite -q postmaster.conf > /dev/null

    echo 'Restarting Apache...'
    service apache2 restart > /dev/null
fi

unset DEBIAN_FRONTEND

echo 'The installation has completed!'