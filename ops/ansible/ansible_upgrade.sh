#!/bin/bash
pip install --upgrade "ansible>=2.0.0.1" setuptools
ansible-playbook -i "localhost," -c local /opt/postmaster/git/ops/ansible/upgrade.yml
