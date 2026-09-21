import os
import sys
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trip.settings')

from django.core.wsgi import get_wsgi_application

_application = get_wsgi_application()

def app(environ, start_response):
    path_info = environ.get('PATH_INFO', '')
    
    # Check if Vercel passed the original path via forwarded headers
    real_uri = environ.get('HTTP_X_FORWARDED_URI') or environ.get('HTTP_X_VERCEL_FORWARDED_PATH') or environ.get('RAW_URI') or environ.get('REQUEST_URI')
    
    if real_uri and not real_uri.startswith('/api/index'):
        real_path = real_uri.split('?')[0]
        if not real_path.startswith('/'):
            real_path = '/' + real_path
        environ['PATH_INFO'] = real_path
    else:
        # Strip /api/index.py, /api/index, or /api prefixes
        for prefix in ['/api/index.py', '/api/index', '/api']:
            if path_info.startswith(prefix):
                path_info = path_info[len(prefix):]
                if not path_info.startswith('/'):
                    path_info = '/' + path_info
                environ['PATH_INFO'] = path_info
                break

    return _application(environ, start_response)
