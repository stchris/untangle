Changelog
---------

Unreleased
- (SECURITY) Use [defusedxml](https://github.com/tiran/defusedxml) to prevent XML SAX vulnerabilities ([#93](https://github.com/stchris/untangle/issues/93))

1.2.0
- (SECURITY) Prevent XML SAX vulnerability: External Entities injection ([#60](https://github.com/stchris/untangle/issues/60))
- support for python keywords as element names ([#43](https://github.com/stchris/untangle/pull/43))
- support Element truthiness on Python 3 ([#68](https://github.com/stchris/untangle/pull/68/))
- dropped support for Python 3.4-3.6 and pypy, untangle currently support Python 3.7-3.10
- fixed setup.py warning ([#77](https://github.com/stchris/untangle/pull/77/))

- dropped support for Python 2.6, 3.3
- formatted code with black
- flake8 linter enforced in CI
- `main` is now the default branch
- switch to Github Actions
- switch to poetry and pytest

1.1.1
- added generic SAX feature toggle ([#26](https://github.com/stchris/untangle/pull/26))
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

