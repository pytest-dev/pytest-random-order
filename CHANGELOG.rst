
--------------
Changelog
--------------

1.2.0
+++++

*2025-06-22*

* Dropped support for EOL Python versions and added support for Python 3.13.
* Fix `#58 <https://github.com/pytest-dev/pytest-random-order/issues/58>`_: ``return`` in a ``finally`` block swallows exceptions and raises a warning in Python 3.14.

1.1.1
+++++

*2024-01-20*

* Fixes #54 - ``AttributeError`` when cacheprovider plugin disabled. Thanks @jhanm12


1.1.0
+++++

*2022-12-03*

* Fixes xdist support (thanks @matejsp)


1.0.4
+++++

*2018-11-30*

* Fixes issues with doctests reported in #36 - ``class``, ``package`` and ``module`` didn't work
  because ``DoctestItem`` doesn't have ``cls`` or ``module`` attributes. Thanks @tobywf.
* Deprecate ``none`` bucket type. **Update**: this was a mistake, it will be kept for backwards compatibility.
* With tox, run tests of pytest-random-order with both pytest 3 and 4.

1.0.3
+++++

*2018-11-16*

* Fixes compatibility issues with pytest 4.0.0, works with pytest 3.0+ as before.
* Tests included in the source distribution.

1.0.0
+++++

*2018-10-20*

* Plugin no longer alters the test order by default. You will have to either 1) pass ``--random-order``,
  or ``--random-order-bucket=<bucket>``, or ``--random-order-seed=<seed>``, or
  2) edit your pytest configuration file and add one of these options
  there under ``addopts``, or 3) specify these flags in environment variable ``PYTEST_ADDOPTS``.
* Python 3.5+ is required. If you want to use this plugin with Python 2.7, use v0.8.0 which is stable and fine
  if you are happy with it randomising the test order by default.
* The name under which the plugin registers itself is changed from ``random-order`` (hyphen) to ``random_order``
  (underscore). This addresses the issue of consistency when disabling or enabling this plugin via the standard
  ``-p`` flag. Previously, the plugin could be disabled by passing ``-p no:random-order`` yet re-enabled
  only by passing ``-p pytest_random_order.plugin``. Now they are ``-p no:random_order``
  to disable and ``-p random_order.plugin`` to enable (The ``.plugin`` bit, I think, is required because
  pytest probably thinks it's an unrelated thing to ``random_order`` and import it, yet without it it's the
  same thing so doesn't import it).


0.8.0
+++++

* pytest cache plugin's ``--failed-first`` works now.
