#!/usr/bin/python
import sys, os
sys.path.insert (0,'/opt/swagmail/git')
os.chdir('/opt/swagmail/git')

activate_this = '/opt/swagmail/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from swagmail import app as application
