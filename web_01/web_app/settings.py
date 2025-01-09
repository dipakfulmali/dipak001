import os
from pathlib import Path

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dipak',
        'USER': 'root',
        'PASSWORD': 'Dipak123@',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

TEMPLATES = [
    {
        # ...existing code...
        'DIRS': [
            BASE_DIR / "web_app" / "templates",
            # ...other directories if any...
        ],
        # ...existing code...
    },
]

MIDDLEWARE = [
    # ...existing code...
    'web_app.middleware.EnsureRegisteredMiddleware',
    # ...existing code...
]
