from tempfile import NamedTemporaryFile
from ..cache import get_cache_key, get_hexdigest, get_hashed_mtime
from ..settings import LESS_EXECUTABLE, LESS_USE_CACHE,\
    LESS_CACHE_TIMEOUT, LESS_OUTPUT_DIR
from ..utils import URLConverter
from django.conf import settings
from django.core.cache import cache
from django.template.base import Library, Node
import logging
import shlex
import subprocess
import os
import sys


logger = logging.getLogger("less")
register = Library()


class InlineLessNode(Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def compile(self, source):


        source_file = NamedTemporaryFile(delete=False)
        source_file.write(source)
        source_file.close()
        args = shlex.split("%s %s" % (LESS_EXECUTABLE, source_file.name))

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, errors = p.communicate()
        os.remove(source_file.name)
        if out:
            return out.decode("utf-8")
        elif errors:
            return errors.decode("utf-8")

        return u""

    def render(self, context):
        output = self.nodelist.render(context)

        if LESS_USE_CACHE:
            cache_key = get_cache_key(get_hexdigest(output))
            cached = cache.get(cache_key, None)
            if cached is not None:
                return cached
            output = self.compile(output)
            cache.set(cache_key, output, LESS_CACHE_TIMEOUT)
            return output
        else:
            return self.compile(output)


@register.tag(name="inlineless")
def do_inlineless(parser, token):
    nodelist = parser.parse(("endinlineless",))
    parser.delete_first_token()
    return InlineLessNode(nodelist)


@register.simple_tag
def less(path):

    try:
        STATIC_ROOT = settings.STATIC_ROOT
    except AttributeError:
        STATIC_ROOT = settings.MEDIA_ROOT

    try:
        STATIC_URL = settings.STATIC_URL
    except AttributeError:
        STATIC_URL = settings.MEDIA_URL

    encoded_full_path = full_path = os.path.join(STATIC_ROOT, path)
    if isinstance(full_path, unicode):
        filesystem_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        encoded_full_path = full_path.encode(filesystem_encoding)

    filename = os.path.split(path)[-1]

    output_directory = os.path.join(STATIC_ROOT, LESS_OUTPUT_DIR, os.path.dirname(path))

    hashed_mtime = get_hashed_mtime(full_path)

    if filename.endswith(".less"):
        base_filename = filename[:-5]
    else:
        base_filename = filename

    output_path = os.path.join(output_directory, "%s-%s.css" % (base_filename, hashed_mtime))

    if not os.path.exists(output_path):
        command = "%s %s" % (LESS_EXECUTABLE, encoded_full_path)
        args = shlex.split(command)
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, errors = p.communicate()
        if out:
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            compiled_file = open(output_path, "w+")
            compiled_file.write(URLConverter(out, os.path.join(STATIC_URL, path)).convert())
            compiled_file.close()

            # Remove old files
            compiled_filename = os.path.split(output_path)[-1]
            for filename in os.listdir(output_directory):
                if filename.startswith(base_filename) and filename != compiled_filename:
                    os.remove(os.path.join(output_directory, filename))
        elif errors:
            logger.error(errors)
            return path

    return output_path[len(STATIC_ROOT):].replace(os.sep, '/').lstrip("/")
