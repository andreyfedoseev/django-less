from django.conf.global_settings import *
import os

DEBUG = True

STATIC_ROOT = MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')
STATIC_URL = MEDIA_URL = "/static/"

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'staticfiles_dir'),
    ("prefix", os.path.join(os.path.dirname(__file__), 'staticfiles_dir_with_prefix')),
)

INSTALLED_APPS = (
    "less",
)

LESS_MTIME_DELAY = 2
LESS_OUTPUT_DIR = "LESS_CACHE"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'less': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

SECRET_KEY = "secret"
