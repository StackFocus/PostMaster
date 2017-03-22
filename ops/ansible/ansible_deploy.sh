#!/bin/bash
rm -rf /opt/postmaster/git/ops/ansible/roles
mkdir /opt/postmaster/git/ops/ansible/roles
pip install --upgrade "ansible>=2.0.0.1" setuptools
# TODO: Should this run by TravisCI instead and included in the .deb package?
ansible-galaxy install -r /opt/postmaster/git/ops/ansible/requirements.yml -p /opt/postmaster/git/ops/ansible/roles/
ansible-playbook -i "localhost," -e postmaster_deb_package=True -c local /opt/postmaster/git/ops/ansible/deploy.yml
