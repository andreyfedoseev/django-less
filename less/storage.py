from django.core.files.storage import FileSystemStorage
from less.settings import LESS_ROOT


class LessFileStorage(FileSystemStorage):
    """
    Standard file system storage for files handled by django-less.

    The default for ``location`` is ``LESS_ROOT``
    """
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = LESS_ROOT
        super(LessFileStorage, self).__init__(location, base_url,
                                                *args, **kwargs)
