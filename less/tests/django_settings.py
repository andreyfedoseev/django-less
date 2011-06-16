from django.conf.global_settings import *
import os


MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')
MEDIA_URL = "/media/"
INSTALLED_APPS = (
    "less",
)
LESS_MTIME_DELAY = 2
LESS_OUTPUT_DIR = "LESS_CACHE"