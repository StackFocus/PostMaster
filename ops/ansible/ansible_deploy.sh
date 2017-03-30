#!/bin/bash
ansible-playbook -i "localhost," -e postmaster_deb_package=True -c local /opt/postmaster/git/ops/ansible/deploy.yml
