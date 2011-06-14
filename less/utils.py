import posixpath
import re
import os


URL_PATTERN = re.compile(r'url\(([^\)]+)\)')


class URLConverter(object):

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
        return URL_PATTERN.sub(self.convert_url, self.content)


