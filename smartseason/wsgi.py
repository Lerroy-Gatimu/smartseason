"""
WSGI config for SmartSeason.
PythonAnywhere will point its WSGI file at this.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartseason.settings')
application = get_wsgi_application()
