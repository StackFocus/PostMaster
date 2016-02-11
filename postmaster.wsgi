#!/usr/bin/python
import sys, os
sys.path.insert (0,'/opt/postmaster/git')
os.chdir('/opt/postmaster/git')

activate_this = '/opt/postmaster/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from postmaster import app as application
