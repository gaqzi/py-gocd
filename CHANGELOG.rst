==========
Change Log
==========

`0.15.1`_ - 2017-05-19
======================

**Changed**

* `PipelineConfig`_ now uses API version 4 by default.

* Fixed schedule failing when requesting new instance and no pipeline triggered, by `@jayste`_

.. _@jayste: https://github.com/jayste

`0.15.0`_ - 2016-11-25
======================

**Added**

* `TemplateConfig`_ API endpoint.

  Added by `@jlyheden`_

.. _TemplateConfig: http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.TemplateConfig
.. _@jlyheden: https://github.com/jlyheden

`0.14.0`_ - 2016-10-13
======================

**Added**

* `PluggableSCM`_ API endpoint.

  Added by `@rogerioyuuki`_

.. _PluggableSCM: http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.PluggableSCM
.. _@rogerioyuuki: https://github.com/rogerioyuuki

`0.13.0`_ - 2016-09-30
======================

**Changed**

* `PipelineConfig`_ now receives an API version, currently defaulting to v2.

  Added by `@henriquegemignani`_

`0.12.1`_ - 2016-06-03
======================

**Changed**

* Fixes failed requests body being lost on Python 3.

  Added by `@henriquegemignani`_


`0.12.0`_ - 2016-XX-XX
======================

**Added**

* `PipelineConfig`_ API endpoint.

  Added by `@henriquegemignani`_

.. _PipelineConfig: http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.PipelineConfig

`0.11.1`_ - 2016-04-19
======================

**Changed**

* Fixes `Pipeline.pause()`_, `Pipeline.unpause()`_, `Pipeline.release()`_, `Pipeline.schedule()`_ and `Stage.cancel()`_ for Go CD 16.3.0.

.. _Pipeline.pause(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Pipeline.pause
.. _Pipeline.unpause(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Pipeline.unpause
.. _Pipeline.release(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Pipeline.release
.. _Stage.cancel(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Stage.cancel

`0.11.0`_ - 2016-02-02
======================

**Added**

* `Stage`_ API endpoint.

  Added by `@henriquegemignani`_

* `Pipeline.stage()`_ helper to get a specific stage from a Pipeline

* `Server.stage()`_ helper to to get a stage for a pipeline

.. _Stage: http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Stage
.. _Pipeline.stage(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Pipeline.stage
.. _Server.stage(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Server.stage

`0.10.0`_ - 2015-11-25
======================

**Added**

* `Pipeline.artifact()`_ helper to get artifacts for the pipeline instance.

* `Pipeline.console_output()`_ helper to get the console output from jobs
  that has finished for a pipeline.

**Changed**

* `Pipeline.instance()`_ now returns the latest instance when ``counter``
  is falsey.

* `Pipeline.schedule()`_ has a new argument, ``return_new_instance`` which
  will return the new instance that was scheduled. The instance information is
  taken from the `Pipeline.history()`_ call and matches the last entry there.

.. _Pipeline.instance(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Pipeline.instance
.. _Pipeline.schedule(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Pipeline.schedule
.. _Pipeline.history(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Pipeline.history
.. _Pipeline.artifact(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Pipeline.artifact
.. _Pipeline.console_output(): http://py-gocd.readthedocs.org/en/latest/gocd.api.html#gocd.api.Pipeline.console_output

`0.9.0`_ - 2015-11-02
=====================

**Added**

* `Artifact`_ API endpoint.

  Added by `@henriquegemignani`_

* Python 3 support

  The API library now works with Python 3, the CLI still needs work for it
  though. *hint hint*

  Added by `@lenniboy`_

A big thanks to @henriquegemignani amd @lenniboy for the patches! :D

.. _Artifact: http://api.go.cd/current/#the-artifact-object
.. _@henriquegemignani: https://github.com/henriquegemignani
.. _@lenniboy: https://github.com/lenniboy

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

.. _`0.15.1`: https://github.com/gaqzi/py-gocd/compare/v0.15.0...v0.15.1
.. _`0.15.0`: https://github.com/gaqzi/py-gocd/compare/v0.14.0...v0.15.0
.. _`0.14.0`: https://github.com/gaqzi/py-gocd/compare/v0.13.0...v0.14.0
.. _`0.13.0`: https://github.com/gaqzi/py-gocd/compare/v0.12.1...v0.13.0
.. _`0.12.1`: https://github.com/gaqzi/py-gocd/compare/v0.12.0...v0.12.1
.. _`0.12.0`: https://github.com/gaqzi/py-gocd/compare/v0.11.1...v0.12.0
.. _`0.11.1`: https://github.com/gaqzi/py-gocd/compare/v0.11.0...v0.11.1
.. _`0.11.0`: https://github.com/gaqzi/py-gocd/compare/v0.10.0...v0.11.0
.. _`0.10.0`: https://github.com/gaqzi/py-gocd/compare/v0.9.0...v0.10.0
.. _`0.9.0`: https://github.com/gaqzi/py-gocd/compare/v0.8.0...v0.9.0
.. _`0.8.0`: https://github.com/gaqzi/py-gocd/compare/v.0.7.1...v0.8.0
.. _`0.7.1`: https://github.com/gaqzi/py-gocd/compare/v0.7.0.2...v.0.7.1
.. _`0.7.0.2`: https://github.com/gaqzi/py-gocd/releases/tag/v0.7.0.2
