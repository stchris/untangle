
.DEFAULT_GOAL=compile

compile:
	python -m compileall -q untangle.py tests/tests.py

test:
	tox

# needs python-stdeb
package_deb:
	python setup.py --command-packages=stdeb.command bdist_deb

clean:
	rm -rf deb_dist/
	rm -rf debian/
	rm -rf dist/
	rm -f untangle-*.tar.gz
