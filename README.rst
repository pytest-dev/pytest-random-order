===================================
pytest-random-order
===================================

.. image:: https://img.shields.io/badge/python-3.7%2C%203.8%2C%203.9%2C%203.10-blue.svg
    :target: https://github.com/jbasko/pytest-random-order

**pytest-random-order** is a `pytest <http://pytest.org>`_ plugin that randomises the order of tests.
This can be useful to detect a test that passes just because it happens to run after an unrelated test that
leaves the system in a *favourable* state.

The plugin allows user to control the level of randomness they want to introduce and to disable
reordering on subsets of tests. Tests can be rerun in a specific order by passing a seed value reported
in a previous test run.

.. image:: https://raw.githubusercontent.com/jbasko/pytest-random-order/master/docs/pytest-random-order-design.png

-----------
Quick Start
-----------

Installation:

::

    $ pip install pytest-random-order

From v1.0.0 onwards, **this plugin no longer randomises tests by default**. To enable randomisation, you have to run
pytest in one of the following ways:

::

    pytest --random-order
    pytest --random-order-bucket=<bucket_type>
    pytest --random-order-seed=<seed>

If you want to always randomise the order of tests, configure pytest. There are many ways to do it,
my favourite one is to add ``addopts = --random-order`` in your project-specific configuration file
under the pytest options (usually ``[pytest]`` or ``[tool:pytest]`` section).

Alternatively, you can set environment variable ``PYTEST_ADDOPTS``:

::

    export PYTEST_ADDOPTS="--random-order"


To randomise the order of tests within modules and shuffle the order of
test modules (which is the default behaviour of the plugin), run pytest as follows:

::

    $ pytest --random-order

To change the scope of re-ordering, run pytest with ``--random-order-bucket=<bucket-type>`` option
where ``<bucket-type>`` can be ``class``, ``module``, ``package``, ``global``:

::

    $ pytest -v --random-order-bucket=package

To disable reordering of tests in a module or class, use pytest marker notation:

::

    pytestmark = pytest.mark.random_order(disabled=True)

To rerun tests in a particular order:

::

    $ pytest -v --random-order-seed=<seed>

All runs in which the randomisation is enabled report seed so if you encounter a specific ordering of tests
that causes problems you can look up the value in the test report and repeat the run with the above command.

::

    platform darwin -- Python 3.5.6, pytest-3.9.1, py-1.7.0, pluggy-0.8.0
    Using --random-order-bucket=module
    Using --random-order-seed=383013

------
Design
------

.. image:: https://raw.githubusercontent.com/jbasko/pytest-random-order/master/docs/pytest-random-order-design.png

The plugin groups tests in buckets, shuffles them within buckets and then shuffles the buckets.

Given the test suite above, here are two of a few possible generated orders of tests:

.. image:: https://raw.githubusercontent.com/jbasko/pytest-random-order/master/docs/pytest-random-order-example1.png

.. image:: https://raw.githubusercontent.com/jbasko/pytest-random-order/master/docs/pytest-random-order-example2.png

You can choose from a few types of buckets:

class
    Tests will be shuffled within a class and classes will be shuffled,
    but tests from one class will never have tests from other classes or modules run in-between them.

module
    Same as above at module level. This is the setting applied if you run pytest with just ``--random-order`` flag
    or ``--random-order-seed=<seed>``.

package
    Same as above at package level. Note that modules (and hence tests inside those modules) that
    belong to package ``x.y.z`` do not belong to package ``x.y``, so they will fall in different buckets
    when randomising with ``package`` bucket type.

parent
    If you are using custom test items which don't belong to any module, you can use this to
    limit reordering of test items to within the ``parent`` to which they belong. For normal test
    functions the parent is the module in which they are declared.

grandparent
    Similar to *parent* above, but use the parent of the parent of the test item as the bucket key instead.

global
    All tests fall in the same bucket, full randomness, tests probably take longer to run.

none
    Disable shuffling. This plugin no longer shuffles tests by default
    so there is nothing to disable, however, there are scenarios where this is useful
    due to the way test configs are specified, see #40.


If you have three buckets of tests ``A``, ``B``, and ``C`` with three tests ``1`` and ``2``, and ``3`` in each of them,
then one of many potential orderings that non-global randomisation can produce could be:

::

    c2, c1, c3, a3, a1, a2, b3, b2, b1

As you can see, all C tests are executed "next" to each other and so are tests in buckets A and B.
Tests from any bucket X are guaranteed to not be interspersed with tests from another bucket Y.
For example, if you choose bucket type ``module`` then bucket X contains all tests that are in this module.

By default, when randomisation is enabled, your tests will be randomised at ``module`` level which means that
tests within a single module X will be executed in no particular order, but tests from
other modules will not be mixed in between tests of module X.

The randomised reordering can be disabled per module or per class irrespective of the chosen bucket type.

--------------
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


Run Last Failed Tests First
+++++++++++++++++++++++++++

Since v0.8.0 pytest cache plugin's ``--failed-first`` flag is supported -- tests that failed in the last run
will be run before tests that passed irrespective of shuffling bucket type.


Disable the Plugin
+++++++++++++++++++++++++++++++++++

If the plugin misbehaves or you just want to assure yourself that it is not the plugin making your tests fail or
pass undeservedly, you can disable it:

::

    $ pytest -p no:random_order

Note that randomisation is disabled by default. By passing ``-p no:random_order`` you are stopping the plugin
from being registered so its hooks won't be registered and its command line options won't appear in ``--help``.


-------
Credits
-------

* The shuffle icon in the diagram is by artist `Daniele De Santis`_ and it was found on
  `iconarchive`_.

* The diagram is drawn with `sketchboard.io`_

.. _Daniele De Santis: https://www.danieledesantis.net/
.. _iconarchive: http://www.iconarchive.com/artist/danieledesantis.html
.. _sketchboard.io: https://sketchboard.io/
