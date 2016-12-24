pytest-random-order
===================================

.. image:: https://travis-ci.org/jbasko/pytest-random-order.svg?branch=master
    :target: https://travis-ci.org/jbasko/pytest-random-order

This is a pytest plugin **to randomise the order** in which tests are run **with some control**
over how much randomness one allows.

Why?
----

It is a good idea to shuffle the order in which your tests run
because a test running early as part of a larger test suite may be leaving
the system under test in a particularly fortunate state for a subsequent test to pass.

How?
----

**pytest-random-order** groups tests in buckets, shuffles them within buckets and then shuffles the buckets.

You can choose from four types of buckets:

class
    Tests from one class will never have tests from other classes or modules run in-between them.

module
    Tests will be shuffled within a module and modules will be shuffled, but tests from one module
    will never be separated by tests from other modules.
    **This is the default setting**.

package
    Same as above, but for package level. Note that modules (and hence tests inside those modules) that
    belong to package ``x.y.z`` do not belong to package ``x.y``, so they will fall in different buckets
    when randomising with ``package`` bucket type.

global
    All tests fall in the same bucket, full randomness, tests probably take longer to run.

If you have three buckets of tests ``A``, ``B``, and ``C`` with three tests ``1`` and ``2``, and ``3`` in each of them,
then here are just two of many potential orderings that non-global randomisation can produce:

::

    C2  C1  C3  A3  A1  A2  B3  B2  B1

    A2  A1  A3  C1  C2  C3  B2  B1  B3

As you can see, all C tests are executed "next" to each other and so are tests in buckets A and B.
Tests from any bucket X are guaranteed to not be interspersed with tests from another bucket Y.
For example, if you choose bucket type ``module`` then bucket X contains all tests that are in this module.

By default, your tests will be randomised at ``module`` level which means that
tests within a single module X will be executed in no particular order, but tests from
other modules will not be mixed in between tests of module X.

The plugin also supports **disabling shuffle on module basis** irrespective of the bucket type
chosen for the test run. See Advanced Options below.

----

Installation
------------

::

    $ pip install pytest-random-order


Usage
-----

The plugin **is enabled by default**.
To randomise the order of tests within modules, just run pytest as always:

::

    $ pytest -v

It is best to start with smallest bucket type (``class`` or ``module`` depending on whether you have class-based tests),
and switch to a larger bucket type when you are sure your tests handle that.

If your tests rely on fixtures that are module or session-scoped, more randomised order of tests will mean slower tests.
You probably don't want to randomise at ``global`` or ``package`` level while you are developing and need a quick confirmation
that nothing big is broken.

::

    $ pytest -v --random-order-bucket=class

    $ pytest -v --random-order-bucket=module

    $ pytest -v --random-order-bucket=package

    $ pytest -v --random-order-bucket=global

If the plugin misbehaves or you just want to assure yourself that it is not the plugin making your tests fail or
pass undeservedly, you can disable it:

::

    $ pytest -p no:random-order -v


Advanced Options
----------------

Disable Shuffling In a Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can disable shuffling of tests within a single module by placing a pytest marker in the module:

::

    pytest.mark.random_order_disabled = True

    def test_number_one():
        pass

    def test_number_two():
        pass

No matter what will be the bucket type for the test run, ``test_number_one`` will always run
before ``test_number_two``.

License
-------

Distributed under the terms of the MIT license, "pytest-random-order" is free and open source software
