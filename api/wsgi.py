import os
import sys
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GMS.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application

# Handle serverless database auto-setup on Vercel
is_vercel = os.environ.get('VERCEL') == '1' or 'VERCEL' in os.environ
if is_vercel and not os.environ.get('DATABASE_URL'):
    try:
        from django.core.management import call_command
        db_path = '/tmp/db.sqlite3'
        source_db = os.path.join(PROJECT_ROOT, 'db.sqlite3')
        if not os.path.exists(db_path):
            if os.path.exists(source_db):
                shutil.copy2(source_db, db_path)
            else:
                call_command('migrate', interactive=False)
    except Exception as e:
        print(f"Vercel DB initialization note: {e}")

