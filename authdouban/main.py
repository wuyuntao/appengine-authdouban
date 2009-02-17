# -*- coding: UTF-8 -*-

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import settings
import urls

if __name__ == '__main__':
    application = webapp.WSGIApplication(urls.urlpatterns, \
                                         debug=settings.DEBUG)
    run_wsgi_app(application)
