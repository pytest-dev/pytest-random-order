pytest-random-order
===================================

**pytest** plugin to randomise the order of tests within module, package, or globally.

This plugin allows you to control the level at which the order of tests is randomised
through ``--random-order-mode`` command line option.

By default, your tests will be randomised at ``module`` level which means that
tests within a single module X will be executed in no particular order, but tests from
other modules will not be mixed in between tests of module X.

Similarly, you can randomise the order of tests at ``package`` and ``global`` levels.

----

Installation
------------

::

    $ pip install pytest-random-order


Usage
-----

::

    $ pytest -v

    $ pytest -v --random-order-mode=global

    $ pytest -v --random-order-mode=package

    $ pytest -v --random-order-mode=module

    $ pytest -v --random-order-mode=class


License
-------

Distributed under the terms of the MIT license, "pytest-random-order" is free and open source software

