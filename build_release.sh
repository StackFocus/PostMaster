#!/bin/bash
#REVISION=`git describe --abbrev=0 --tags | cut -c 2-`
REVISION=1.1.0
fpm -s dir -t deb -n "postmaster" -v $REVISION \
--prefix /opt/postmaster/git \
--description 'PostMaster is a beautiful web application to manage domains, users, and aliases on a Linux mail server' \
--url 'https://github.com/StackFocus/PostMaster' \
--maintainer 'StackFocus <hello@stackfocus.org>' \
--vendor 'StackFocus' \
--license 'AGPL' \
--deb-changelog './docs/ChangeLog.md' \
--after-install ops/ansible/ansible_install.sh \
--after-upgrade ops/ansible/ansible_upgrade.sh \
--exclude env \
--exclude .git \
--exclude .vagrant \
--deb-no-default-config-files \
-d git -d python -d python-pip -d python-dev -d python-virtualenv \
-d libldap2-dev -d libssl-dev -d libsasl2-dev -d libffi-dev \
-d apache2 -d libapache2-mod-wsgi -d libmysqlclient-dev ./
ls -la | grep *.deb
