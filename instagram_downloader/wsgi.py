"""
WSGI config for instagram_downloader project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_downloader.settings')
    from django.core.management import execute_from_command_line
    import sys
    port = os.getenv('PORT', '8000')  # Use the PORT environment variable if available, else default to 8000
    execute_from_command_line(sys.argv + ['runserver', f'0.0.0.0:{port}'])

