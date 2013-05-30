from django.conf import settings


LESS_EXECUTABLE = getattr(settings, "LESS_EXECUTABLE", "lessc")
LESS_USE_CACHE = getattr(settings, "LESS_USE_CACHE", True)
LESS_CACHE_TIMEOUT = getattr(settings, "LESS_CACHE_TIMEOUT", 60 * 60 * 24 * 30) # 30 days
LESS_MTIME_DELAY = getattr(settings, "LESS_MTIME_DELAY", 10) # 10 seconds
LESS_ROOT = getattr(settings, "LESS_ROOT", getattr(settings, "STATIC_ROOT", getattr(settings, "MEDIA_ROOT")))
LESS_OUTPUT_DIR = getattr(settings, "LESS_OUTPUT_DIR", "LESS_CACHE")
LESS_OPTIONS = getattr(settings, "LESS_OPTIONS", [])
LESS_DEVMODE = getattr(settings, "LESS_DEVMODE", False)
LESS_DEVMODE_WATCH_DIRS = getattr(settings, "LESS_DEVMODE_WATCH_DIRS", [settings.STATIC_ROOT])
LESS_DEVMODE_EXCLUDE = getattr(settings, "LESS_DEVMODE_EXCLUDE", ())
