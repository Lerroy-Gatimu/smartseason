import sys
import os

# Replace with your actual PythonAnywhere username
path = '/home/YOUR_USERNAME/smartseason'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'smartseason.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['SECRET_KEY'] = 'p^wub69xvh00^yp5$p2n2w#tn!g+xi$kug-pd&@qd3tk3z#dk9'

os.environ['DB_NAME']     = 'smartseason_db'
os.environ['DB_USER']     = 'root'
os.environ['DB_PASSWORD'] = 'lerroy'
os.environ['DB_HOST']     = 'localhost'
os.environ['DB_PORT']     = '3306'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()