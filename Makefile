
.DEFAULT_GOAL=compile

compile:
	python -m compileall -q untangle.py tests/tests.py

setup:
	python -m pip install poetry
	poetry install

lint:
	poetry run flake8 .
	poetry run black --check .

test:
	poetry run pytest -v

# needs python-stdeb
package_deb:
	python setup.py --command-packages=stdeb.command bdist_deb

clean:
	rm -rf deb_dist/
	rm -rf debian/
	rm -rf dist/
	rm -f untangle-*.tar.gz
