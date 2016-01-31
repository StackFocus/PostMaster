#!/usr/bin/python
import sys, os
sys.path.insert (0,'/var/www/SwagMail')
os.chdir("/var/www/SwagMail")

from swagmail import app as application
