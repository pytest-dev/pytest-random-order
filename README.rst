pytest-random-order
===================================

.. image:: https://img.shields.io/badge/python-2.6%2C%202.7%2C%203.5-blue.svg
    :target: https://github.com/jbasko/pytest-random-order

.. image:: https://img.shields.io/badge/coverage-98%25-green.svg
    :target: https://github.com/jbasko/pytest-random-order

.. image:: https://travis-ci.org/jbasko/pytest-random-order.svg?branch=master
    :target: https://travis-ci.org/jbasko/pytest-random-order

pytest-random-order is a plugin for `pytest <http://pytest.org>`_ that randomises the order in which
tests are run to reveal unwanted coupling between tests. The plugin allows user to control the level
of randomness they want to introduce and to disable reordering on subsets of tests.
Tests can be rerun in a specific order by passing a seed value reported in a previous test run.


Quick Start
-----------

::

    $ pip install pytest-random-order

The plugin **is enabled by default**. To randomise the order of tests within modules and shuffle the order of
test modules (which is the default behaviour of the plugin), just run pytest as always:

::

    $ pytest -v

To change the level of randomness allowed, run pytest with ``--random-order-bucket=<bucket-type>`` option
where ``<bucket-type>`` can be ``class``, ``module``, ``package``, or ``global``:

::

    $ pytest -v --random-order-bucket=package

To disable reordering of tests in a module or class, use pytest marker notation:

::

    pytestmark = pytest.mark.random_order(disabled=True)

To rerun tests in a particular order:

::

    $ pytest -v --random-order-seed=<value-reported-in-previous-run>


Design
------

pytest-random-order plugin groups tests in buckets, shuffles them within buckets and then shuffles the buckets.

You can choose from four types of buckets:

class
    Tests will be shuffled within a class and classes will be shuffled,
    but tests from one class will never have tests from other classes or modules run in-between them.

module
    Same as above at module level. **This is the default setting**.

package
    Same as above at package level. Note that modules (and hence tests inside those modules) that
    belong to package ``x.y.z`` do not belong to package ``x.y``, so they will fall in different buckets
    when randomising with ``package`` bucket type.

global
    All tests fall in the same bucket, full randomness, tests probably take longer to run.

If you have three buckets of tests ``A``, ``B``, and ``C`` with three tests ``1`` and ``2``, and ``3`` in each of them,
then one of many potential orderings that non-global randomisation can produce could be:

::

    c2, c1, c3, a3, a1, a2, b3, b2, b1

As you can see, all C tests are executed "next" to each other and so are tests in buckets A and B.
Tests from any bucket X are guaranteed to not be interspersed with tests from another bucket Y.
For example, if you choose bucket type ``module`` then bucket X contains all tests that are in this module.

By default, your tests will be randomised at ``module`` level which means that
tests within a single module X will be executed in no particular order, but tests from
other modules will not be mixed in between tests of module X.

The randomised reordering can be disabled per module or per class irrespective of the chosen bucket type.

Usage and Tips
--------------

Bucket Type Choice
++++++++++++++++++

It is best to start with smallest bucket type (``class`` or ``module`` depending on whether you have class-based tests),
and switch to a larger bucket type when you are sure your tests handle that.

If your tests rely on fixtures that are module or session-scoped, more randomised order of tests will mean slower tests.
You probably don't want to randomise at ``global`` or ``package`` level while you are coding and need a quick confirmation
that nothing big is broken.

Disable Shuffling in Module or Class
++++++++++++++++++++++++++++++++++++

You can disable shuffling of tests within a single module or class by marking the module or class
with ``random_order`` marker and passing ``disabled=True`` to it:

::

    pytestmark = pytest.mark.random_order(disabled=True)

    def test_number_one():
        assert True

    def test_number_two():
        assert True

::

    class MyTest(TestCase):
        pytestmark = pytest.mark.random_order(disabled=True)

        def test_number_one(self):
            self.assertTrue(True)


No matter what will be the bucket type for the test run, ``test_number_one`` will always run
before ``test_number_two``.


Rerun Tests in the Same Order (Same Seed)
+++++++++++++++++++++++++++++++++++++++++

If you discover a failing test because you reordered tests, you will probably want to be able to rerun the tests
in the same failing order. To allow reproducing test order, the plugin reports the seed value it used with pseudo random number
generator:

::

    ============================= test session starts ==============================
    ..
    Using --random-order-bucket=module
    Using --random-order-seed=24775
    ...

You can now use the ``--random-order-seed=...`` bit as an argument to the next run to produce the same order:

::

    $ pytest -v --random-order-seed=24775


Disable the Plugin
++++++++++++++++++

If the plugin misbehaves or you just want to assure yourself that it is not the plugin making your tests fail or
pass undeservedly, you can disable it:

::

    $ pytest -p no:random-order -v

Thanks
++++++

Thanks **Raul Gallegos** (eLRuLL) for adding Python 2.6 support.

License
-------

Distributed under the terms of the MIT license, "pytest-random-order" is free and open source software
