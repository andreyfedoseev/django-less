from less.settings import LESS_EXECUTABLE, LESS_OUTPUT_DIR
from django.conf import settings
import logging
import posixpath
import re
import os
import subprocess


logger = logging.getLogger("less")


STATIC_ROOT = getattr(settings, "STATIC_ROOT", getattr(settings, "STATIC_ROOT"))
STATIC_URL = getattr(settings, "STATIC_URL", getattr(settings, "MEDIA_URL"))


class URLConverter(object):

    URL_PATTERN = re.compile(r'url\(([^\)]+)\)')

    def __init__(self, content, source_path):
        self.content = content
        self.source_dir = os.path.dirname(source_path)

    def convert_url(self, matchobj):
        url = matchobj.group(1)
        url = url.strip(' \'"')
        if url.startswith(('http://', 'https://', '/', 'data:')):
            return "url('%s')" % url
        full_url = posixpath.normpath("/".join([self.source_dir, url]))
        return "url('%s')" % full_url

    def convert(self):
        return self.URL_PATTERN.sub(self.convert_url, self.content)


def compile_less(input, output, less_path):

    less_root = os.path.join(STATIC_ROOT, LESS_OUTPUT_DIR)
    if not os.path.exists(less_root):
        os.makedirs(less_root)

    args = [LESS_EXECUTABLE, input]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, errors = p.communicate()

    if errors:
        logger.error(errors)
        return False

    output_directory = os.path.dirname(output)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    compiled_file = open(output, "w+")
    compiled_file.write(URLConverter(out, os.path.join(STATIC_URL, less_path)).convert())
    compiled_file.close()

    return True
