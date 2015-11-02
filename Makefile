.PHONY: develop docs test coverage clean lint pre-commit upload-package dist

default: coverage

develop:
	python setup.py develop
	pip install -r test-requirements.txt
	pip install flake8 restructuredtext_lint
	@echo "#!/bin/bash\nmake pre-commit" > .git/hooks/pre-push
	@chmod a+x .git/hooks/pre-push
	@echo
	@echo "Added pre-push hook! To run manually: make pre-commit"

setup-env:
	@[ "$(SNAP_CI)" = 'true' ] && \
		export PATH="$PATH:/opt/local/python/3.3.5/bin:/opt/local/python/3.4.0/bin:/opt/local/python/3.5.0/bin" \
		|| true

test: setup-env
	tox

coverage:
	py.test --cov=gocd tests

coverage-html: coverage clean-coverage-html
	coverage html

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-coverage-html:
	rm -rf htmlcov

clean-docs:
	@cd docs && \
	  make clean

clean: clean-pyc clean-build clean-coverage-html clean-docs

docs:
	@cd docs && \
	  make html

lint-rst:
	rst-lint README.rst CHANGELOG.rst

lint-pep8:
	flake8 gocd tests

lint: lint-rst lint-pep8

pre-commit: coverage lint

develop-dist:
	pip2 install wheel
	pip3 install wheel

sdist:
	python setup.py sdist

bdist_py2:
	python2 setup.py bdist_wheel

bdist_py3:
	python3 setup.py bdist_wheel

bdist: bdist_py2 bdist_py3

dist: develop-dist sdist bdist

upload-package: lint clean dist
	pip install twine
	twine upload dist/*

rpm: clean
	python setup.py bdist_rpm --provides 'Python(gocd)'
