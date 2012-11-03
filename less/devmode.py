from less.utils import compile_less, logger
from less.settings import LESS_DEVMODE_WATCH_DIRS, LESS_OUTPUT_DIR, LESS_DEVMODE_EXCLUDE
from django.conf import settings
import os
import re
import sys
import time
import threading


try:
    STATIC_ROOT = settings.STATIC_ROOT
except AttributeError:
    STATIC_ROOT = settings.MEDIA_ROOT


WATCHED_FILES = {}
LESS_IMPORT_RE = re.compile(r"""@import\s+['"](.+?\.less)['"]\s*;""")


def daemon():

    while True:
        to_be_compiled = set()
        for watched_dir in LESS_DEVMODE_WATCH_DIRS:
            for root, dirs, files in os.walk(watched_dir):
                for filename in filter(lambda f: f.endswith(".less"), files):
                    filename = os.path.join(root, filename)
                    f = os.path.relpath(filename, STATIC_ROOT)
                    if f in LESS_DEVMODE_EXCLUDE:
                        continue
                    mtime = os.path.getmtime(filename)

                    if f not in WATCHED_FILES:
                        WATCHED_FILES[f] = [None, set()]

                    if WATCHED_FILES[f][0] != mtime:
                        WATCHED_FILES[f][0] = mtime
                        # Look for @import statements to update dependecies
                        for line in open(filename):
                            for imported in LESS_IMPORT_RE.findall(line):
                                imported = os.path.relpath(os.path.join(os.path.dirname(filename), imported), STATIC_ROOT)
                                if imported not in WATCHED_FILES:
                                    WATCHED_FILES[imported] = [None, set([f])]
                                else:
                                    WATCHED_FILES[imported][1].add(f)

                        to_be_compiled.add(f)
                        importers = WATCHED_FILES[f][1]
                        while importers:
                            for importer in importers:
                                to_be_compiled.add(importer)
                            importers = WATCHED_FILES[importer][1]

        for less_path in to_be_compiled:
            full_path = os.path.join(STATIC_ROOT, less_path)
            base_filename = os.path.split(less_path)[-1][:-5]
            output_directory = os.path.join(STATIC_ROOT, LESS_OUTPUT_DIR, os.path.dirname(less_path))
            output_path = os.path.join(output_directory, "%s.css" % base_filename)
            if isinstance(full_path, unicode):
                filesystem_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
                full_path = full_path.encode(filesystem_encoding)

            compile_less(full_path, output_path, less_path)
            logger.debug("Compiled: %s" % less_path)

        time.sleep(1)


def start_daemon():
    thread = threading.Thread(target=daemon)
    thread.daemon = True
    thread.start()
