"""
WSGI config for sysproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sysproject.settings')

application = get_wsgi_application()

# Run migrations automatically on startup
import django
django.setup()
from django.core.management import call_command
try:
    call_command('migrate', interactive=False)
    print("✅ Database migrations applied successfully")
except Exception as e:
    print("⚠️ Error applying migrations:", e)