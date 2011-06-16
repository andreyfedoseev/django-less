from unittest import main, TestCase
from django.template.base import Template
from django.template.context import RequestContext
import os
import re
import time
import shutil


os.environ["DJANGO_SETTINGS_MODULE"] = "less.tests.django_settings"


class LessTestCase(TestCase):

    def setUp(self):
        from django.conf import settings as django_settings
        self.django_settings = django_settings

        output_dir = os.path.join(self.django_settings.MEDIA_ROOT,
                                  self.django_settings.LESS_OUTPUT_DIR)

        # Remove the output directory if it exists to start from scratch
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def test_inline_less(self):
        template = Template("""
        {% load less %}
        {% inlineless %}
            @the-border: 1px;
            #bordered {
                border: @the-border * 2;
            }
        {% endinlineless %}
        """)
        rendered = """#bordered {
  border: 2px;
}"""
        self.assertEqual(template.render(RequestContext({})).strip(), rendered)

    def test_external_less(self):

        template = Template("""
        {% load less %}
        {% less "styles/test.less" %}
        """)
        compiled_filename_re = re.compile(r"LESS_CACHE/styles/test-[a-f0-9]{12}.css")
        compiled_filename = template.render(RequestContext({})).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename)))

        compiled_path = os.path.join(self.django_settings.MEDIA_ROOT, compiled_filename)
        compiled_content = open(compiled_path).read().strip()
        compiled = """#header h1 {
  background-image: url('/media/images/header.png');
}"""
        self.assertEquals(compiled_content, compiled)

        # Change the modification time
        source_path = os.path.join(self.django_settings.MEDIA_ROOT, "styles/test.less")
        os.utime(source_path, None)

        # The modification time is cached so the compiled file is not updated
        compiled_filename_2 = template.render(RequestContext({})).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename_2)))
        self.assertEquals(compiled_filename, compiled_filename_2)

        # Wait to invalidate the cached modification time
        time.sleep(self.django_settings.LESS_MTIME_DELAY)

        # Now the file is re-compiled
        compiled_filename_3 = template.render(RequestContext({})).strip()
        self.assertTrue(bool(compiled_filename_re.match(compiled_filename_3)))
        self.assertNotEquals(compiled_filename, compiled_filename_3)

        # Check that we have only one compiled file, old files should be removed

        compiled_file_dir = os.path.dirname(os.path.join(self.django_settings.MEDIA_ROOT,
                                                         compiled_filename_3))
        self.assertEquals(len(os.listdir(compiled_file_dir)), 1)


if __name__ == '__main__':
    main()