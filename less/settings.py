from django.conf import settings


LESS_BIN = getattr(settings, "LESS_BIN", "lessc")
LESS_USE_CACHE = getattr(settings, "LESS_USE_CACHE", True)
LESS_CACHE_TIMEOUT = getattr(settings, "LESS_CACHE_TIMEOUT", 60 * 60 * 24 * 30) # 30 days
LESS_MTIME_DELAY = getattr(settings, "LESS_MTIME_DELAY", 10) # 10 seconds
LESS_OUTPUT_DIR = getattr(settings, "LESS_OUTPUT_DIR", "LESS_CACHE")