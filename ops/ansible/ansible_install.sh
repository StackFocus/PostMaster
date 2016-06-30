#!/bin/bash
pip install --upgrade ansible setuptools
ansible-playbook -i "localhost," -c local /opt/postmaster/git/ops/ansible/site.yml
