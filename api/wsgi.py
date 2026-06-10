import os
import sys

from django.core.wsgi import get_wsgi_application

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GMS.settings')

application = get_wsgi_application()


def handler(request):
    from vercel_wsgi import VercelWSGI

    return VercelWSGI(application).handle(request)
