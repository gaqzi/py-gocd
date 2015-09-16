==========
Change Log
==========

WIP - Some point
================

Added
-----

* An option ``request_debug_level`` on ``gocd.Server`` to set log level
`0.7.1`_ - 2015-08-23
=====================

Changed
-------

* Change values that makes a request into a POST request:

    - Any string (even empty)
    - Any dict (even empty)
    - True (which converts into an empty string)

  This is a bug fix that came about because of differences between
  different Python versions, 2.6 handled empty dicts differently in
  urllib2 compared to 2.7, see `pr #2`_ for details.

  Thanks to @henriquegemignani for reporting and providing a fix!

.. _`pr #2`: https://github.com/gaqzi/py-gocd/pull/2

`0.7.0.2`_ - 2015-08-09
=======================

Nothing much to say here, initial public release. :)

.. _`0.7.1`: https://github.com/gaqzi/py-gocd/compare/v0.7.0.2...v0.7.1
.. _`0.7.0.2`: https://github.com/gaqzi/py-gocd/releases/tag/v0.7.0.2
