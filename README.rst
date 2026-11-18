A Python API for interacting with `Go Continuous Delivery`_
===========================================================

.. image:: http://codecov.io/github/gaqzi/py-gocd/coverage.svg?branch=master
   :target: http://codecov.io/github/gaqzi/py-gocd?branch=master
   :alt: Coverage Status

.. image:: https://snap-ci.com/gaqzi/py-gocd/branch/master/build_image
   :target: https://snap-ci.com/gaqzi/py-gocd/branch/master
   :alt: Build Status

.. image:: https://readthedocs.org/projects/py-gocd/badge/?version=latest
   :target: http://py-gocd.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/gocd.svg
   :target: https://pypi.python.org/pypi/gocd/
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/dm/gocd.svg
   :target: https://pypi.python.org/pypi/gocd/
   :alt: Downloads

.. image:: https://img.shields.io/pypi/pyversions/gocd.svg
   :target: https://pypi.python.org/pypi/gocd/
   :alt: Python versions

.. image:: https://img.shields.io/pypi/status/gocd.svg
   :target: https://pypi.python.org/pypi/gocd/
   :alt: Package status

The reason for this project is to provide a wrapper to easily perform operations
against Go. I've been writing a lot of shell scripts to interact with Go using
curl, but when going a little further than the most basic interactions I've
always started to feel the need for doing all of this in a proper programming
language. I.e. something that is beyond bash.

The project now requires Python 3.12.x and a new external dependency urllib3 https://pypi.org/project/urllib3/ to work.

Anyone wanting to upgrade to this new version can do it easily via running this simple bash script
"scripts/test_upgrade_to_python3.sh".
This should take care of installing new dependency, upgrading new ones, installing test
dependencies and running the tests for you to be able to confidently deploy it on your systems.

This library was created to support `a Go CLI`__, to handle some common
scenarios you as an admin or advanced user would do.

`API documentation`_ available on read the docs.

.. __: https://github.com/gaqzi/gocd-cli/
.. _`API documentation`: http://py-gocd.readthedocs.org/en/latest/

Usage
-----

The main interaction point for this library is the `Server` class,
it contains helpers to instantiate the different API endpoints.

An example interaction:

.. code-block:: python

    >>> from gocd import Server
    >>> server = Server('http://localhost:8153', user='admin', password='badger')
    >>> pipeline = server.pipeline('up42')
    >>> response = pipeline.history()
    >>> bool(response)
    True
    >>> response.status_code
    200
    >>> response.content_type
    'application/vnd.go.cd.v1+json'
    >>> response.is_ok
    True
    >>> response.body
    {'_links': {'next': {'href': 'http://localhost:8153/go/api/pipelines/up42/history?after=206
    '}}, 'pipelines':[...]}

Style
-----

This project aims to follow the `Google Python Style Guide`_ and particularly
the section on `commenting the code`_.

Versioning
----------

`Semantic versioning`_ is used.

License
-------

MIT License.

.. _`Go Continuous Delivery`: http://go.cd/
.. _`Google Python Style Guide`: https://google-styleguide.googlecode.com/svn/trunk/pyguide.html
.. _`commenting the code`: https://google-styleguide.googlecode.com/svn/trunk/pyguide.html?showone=Comments#Comments
.. _Semantic versioning: http://semver.org/
