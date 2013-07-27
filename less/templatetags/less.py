from tempfile import NamedTemporaryFile
from ..cache import get_cache_key, get_hexdigest, get_hashed_mtime
from ..utils import compile_less
from ..settings import LESS_EXECUTABLE, LESS_USE_CACHE,\
    LESS_CACHE_TIMEOUT, LESS_ROOT, LESS_OUTPUT_DIR, LESS_DEVMODE,\
    LESS_DEVMODE_WATCH_DIRS
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.cache import cache
from django.template.base import Library, Node, TemplateSyntaxError
import logging
import subprocess
import os
import sys


STATIC_ROOT = getattr(settings, "STATIC_ROOT", getattr(settings, "MEDIA_ROOT"))


logger = logging.getLogger("less")


register = Library()


class InlineLessNode(Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def compile(self, source):
        source_file = NamedTemporaryFile(delete=False)
        source_file.write(source)
        source_file.close()
        args = [LESS_EXECUTABLE, source_file.name]

        popen_kwargs = dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if os.name == "nt":
            popen_kwargs["shell"] = True

        p = subprocess.Popen(args, **popen_kwargs)
        out, errors = p.communicate()
        os.remove(source_file.name)
        if out:
            return out.decode(settings.FILE_CHARSET)
        elif errors:
            return errors.decode(settings.FILE_CHARSET)

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


def less_paths(path):

    full_path = os.path.join(STATIC_ROOT, path)

    if settings.DEBUG and not os.path.exists(full_path):
        # while developing it is more confortable
        # searching for the less files rather then
        # doing collectstatics all the time
        full_path = finders.find(path)

        if full_path is None:
            raise TemplateSyntaxError("Can't find staticfile named: {}".format(path))

    file_name = os.path.split(path)[-1]
    output_dir = os.path.join(LESS_ROOT, LESS_OUTPUT_DIR, os.path.dirname(path))

    return full_path, file_name, output_dir


@register.simple_tag
def less(path):

    logger.info("processing file %s" % path)

    full_path, file_name, output_dir = less_paths(path)
    base_file_name = os.path.splitext(file_name)[0]

    if LESS_DEVMODE and any(map(lambda watched_dir: full_path.startswith(watched_dir), LESS_DEVMODE_WATCH_DIRS)):
        return os.path.join(os.path.dirname(path), "%s.css" % base_file_name)

    hashed_mtime = get_hashed_mtime(full_path)
    output_file = "%s-%s.css" % (base_file_name, hashed_mtime)
    output_path = os.path.join(output_dir, output_file)

    encoded_full_path = full_path
    if isinstance(full_path, unicode):
        filesystem_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        encoded_full_path = full_path.encode(filesystem_encoding)

    if not os.path.exists(output_path):
        compile_less(encoded_full_path, output_path, path)

        # Remove old files
        compiled_filename = os.path.split(output_path)[-1]
        for filename in os.listdir(output_dir):
            if filename.startswith(base_file_name) and filename != compiled_filename:
                os.remove(os.path.join(output_dir, filename))

    return os.path.join(LESS_OUTPUT_DIR, os.path.dirname(path), output_file)
