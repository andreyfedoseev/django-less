Changes
*******

Dev
----

- Add LESS_OPTIONS config variable.
- Use urlparse instead of posixpath to leave double slashes in urls.
- Raise exception on compilation errors.


0.7.1
------

- Use hashlib instead of django.utils.hashcompat which is deprecated in Django 1.5
- Add `shell=True` to Popen arguments when running on Windows.


0.7
----

- Add staticfiles finder to serve compiled files in dev mode


0.6
----

- Add LESS_ROOT setting


0.5.1
-----

- Fix unicodedecodeerror with non ascii in less file


0.5
----

- Switch to staticfiles.finders when looking up the files in DEBUG mode.


0.4
----

- Add support for lookup in STATICFILES_DIRS


0.3
----

- Log LESS compilation errors
- Fixed bug with paths on Windows


0.2
----

- Use STATIC_ROOT / STATIC_URL settings when possible instead of MEDIA_ROOT / MEDIA_URL


0.1
----

- Initial release
