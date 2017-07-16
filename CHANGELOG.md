Changelog
---------

Unreleased
- flake8 now runs as part of the unit tests. Fully replaced nose with tox as a test runner.
- support for python keywords as element names ([#43](https://github.com/stchris/untangle/pull/43))

1.1.1
- addded generic SAX feature toggle ([#26](https://github.com/stchris/untangle/pull/26))
- added support for `hasattribute`/`getattribute` ([#15](https://github.com/stchris/untangle/pull/15))
- added support for `len()` on parsed objects ([https://github.com/stchris/untangle/commit/31f3078]())
- fixed a potential bug when trying to detect URLs ([https://github.com/stchris/untangle/commit/cfa11d16]())
- include CDATA in `str` representation ([https://github.com/stchris/untangle/commit/63aaa]())
- added support for parsing file-like objects ([#9](https://github.com/stchris/untangle/issues/9))
- dropped support for Python 3.2 (untangle now supports Python versions 2.6, 2.7, 3.3, 3.4, 3.5, 3.6 and pypy)
- improved unit test coverage and quality
- better documentation and examples for accessing cdata

1.1.0
- __dir__ support for untangled objects
- code cleanups

1.0.0
- first official release

