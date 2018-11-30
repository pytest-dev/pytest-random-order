# -*- coding: utf-8 -*-
import py
import pytest


@pytest.fixture
def tmp_tree_of_tests(testdir):
    """
    Creates a directory structure:
        tmpdir/
            foo.py

    """

    utils_package = testdir.mkpydir('utils')
    utils_package.join('__init__.py').write('')

    utils_package.join('foo.py').write(py.code.Source('''
        def add(a, b):
            """
            >>> add(1, 1)
            2
            >>> add(0, 0)
            0
            """
            return a + b

        def subtract(a, b):
            """
            >>> subtract(1, 1)
            0
            >>> subtract(0, 2)
            -2
            """
            return a - b
    '''))

    return testdir


@pytest.mark.parametrize('bucket', [
    'global',
    'package',
    'module',
    'class',
    'parent',
    'grandparent',
    'none',
])
def test_doctests(tmp_tree_of_tests, get_test_calls, bucket):
    result1 = tmp_tree_of_tests.runpytest(
        '--doctest-modules', '--random-order-bucket={0}'.format(bucket), '--verbose', '-s',
    )
    result1.assert_outcomes(passed=2, failed=0)
    assert 'PytestWarning' not in result1.stdout.str()
    assert 'PytestWarning' not in result1.stderr.str()
