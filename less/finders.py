from less.storage import LessFileStorage
from django.contrib.staticfiles.finders import BaseStorageFinder


class LessFinder(BaseStorageFinder):
    """
    A staticfiles finder that looks in LESS_ROOT
    for compiled files, to be used during development
    with staticfiles development file server or during
    deployment.
    """
    storage = LessFileStorage

    def list(self, ignore_patterns):
        return []
