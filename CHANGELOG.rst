==========
Change Log
==========

`0.8.0`_ - 2015-09-16
=====================


Added
-----

* An option ``request_debug_level`` on ``gocd.Server`` to set log level
* Set the session cookie when a request finishes if it hasn't been set.

  This is intended to speed up subsequent requests to Go and will
  `according to the documentation`_ give a significant speed improvement
  for certain auth modules.
* `Pipeline groups`_ API endpoint added. This is used primarily now for
  getting a list of all available pipelines in `gocd-cli`_ and as such
  only has nice helpers for that use case. Suggestions welcome for more
  useful wrappers here. :)

.. _according to the documentation: http://api.go.cd/current/#cookie-session-authentication
.. _Pipeline groups: http://api.go.cd/current/#pipeline-groups
.. _gocd-cli: https://github.com/gaqzi/gocd-cli/

Fixed
-----

* Set the session cookie properly, Go will now not force another login
  after the session has been set

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

.. _`0.8.0`: https://github.com/gaqzi/py-gocd/compare/v.0.7.1...v0.8.0
.. _`0.7.1`: https://github.com/gaqzi/py-gocd/compare/v0.7.0.2...v.0.7.1
.. _`0.7.0.2`: https://github.com/gaqzi/py-gocd/releases/tag/v0.7.0.2
