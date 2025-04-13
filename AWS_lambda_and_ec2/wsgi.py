# Wsgi.py 
# It serves as the entry point for the web server to communicate with your web application using the WSGI interface.

#code

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/html/MusicApp")

from app import app as application
