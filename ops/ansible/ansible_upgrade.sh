#!/bin/bash
pip install ansible
ansible-playbook -i "localhost," -c local /opt/postmaster/git/ops/ansible/upgrade.yml
