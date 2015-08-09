A Python API for interacting with `Go Continuous Delivery`_
===========================================================

The reason for this project is to provide a wrapper to easily perform operations
against Go. I've been writing a lot of shell scripts to interact with Go using
curl, but when going a little further than the most basic interactions I've
always started to feel the need for doing all of this in a proper programming
language. I.e. something that is not bash.

I've chosen to use Python and version 2.6.6 as my target platform, with no
external dependencies, to make it really straightforward to install/run on RHEL6
and other similar *stable* distributions.

Usage
-----

The main interaction point for this library is the `Server` class,
it contains helpers to instantiate the different API endpoints.

An example interaction:

.. code-block:: python

    >>> from gocd import Server
    >>> server = Server('http://localhost:8153', user='ba', password='secret')
    >>> pipeline = server.pipeline('Example-Pipeline')
    >>> response = pipeline.history()
    >>> bool(response)
    True
    >>> response.status_code
    200
    >>> response.content_type
    'application/json'
    >>> response.is_ok
    >>> response.body
    {"pagination":{"offset":0,"total":1,"page_size":10},"pipelines":[...]"}

Style
-----

This project aims to follow the `Google Python Style Guide`_ and particularly
the section on `commenting the code`_.

License
-------

MIT License.

.. _`Go Continuous Delivery`: http://go.cd/
.. _`Google Python Style Guide`: https://google-styleguide.googlecode.com/svn/trunk/pyguide.html
.. _`commenting the code`: https://google-styleguide.googlecode.com/svn/trunk/pyguide.html?showone=Comments#Comments
