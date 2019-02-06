#!/usr/bin/python
import sys
sys.path.insert(0, '/var/www/catalog.udacity.swmo.ch/')

from app import app as application
application.root_path = '/var/www/catalog.udacity.swmo.ch/'
application.secret_key = 'fklsjfdlajiejrkaejrklajlnIE((*HFUFHU'
