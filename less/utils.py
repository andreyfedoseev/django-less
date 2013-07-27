from less import LessException
from less.settings import LESS_EXECUTABLE, LESS_ROOT, LESS_OUTPUT_DIR, \
        LESS_OPTIONS
from django.conf import settings
import logging
import urlparse
import re
import os
import subprocess


logger = logging.getLogger("less")


STATIC_URL = getattr(settings, "STATIC_URL", getattr(settings, "MEDIA_URL"))


class URLConverter(object):

    URL_PATTERN = re.compile(r'url\(([^\)]+)\)')

    def __init__(self, content, source_path):
        self.content = content
        self.source_dir = os.path.dirname(source_path)
        if not self.source_dir.endswith('/'):
            self.source_dir = self.source_dir + '/'

    def convert_url(self, matchobj):
        url = matchobj.group(1)
        url = url.strip(' \'"')
        if url.startswith(('http://', 'https://', '/', 'data:')):
            return "url('%s')" % url
        return "url('%s')" % urlparse.urljoin(self.source_dir, url)

    def convert(self):
        return self.URL_PATTERN.sub(self.convert_url, self.content)


def compile_less(input, output, less_path):

    less_root = os.path.join(LESS_ROOT, LESS_OUTPUT_DIR)
    if not os.path.exists(less_root):
        os.makedirs(less_root)

    args = [LESS_EXECUTABLE] + LESS_OPTIONS + [input]
    popen_kwargs = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if os.name == "nt":
        popen_kwargs["shell"] = True
    p = subprocess.Popen(args, **popen_kwargs)
    out, errors = p.communicate()

    if errors:
        logger.error(errors)
        raise LessException(errors)

    output_directory = os.path.dirname(output)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    compiled_css = URLConverter(
        out.decode(settings.FILE_CHARSET),
        os.path.join(STATIC_URL, less_path)
    ).convert()
    compiled_file = open(output, "w+")
    compiled_file.write(compiled_css.encode(settings.FILE_CHARSET))
    compiled_file.close()
