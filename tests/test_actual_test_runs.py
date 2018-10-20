# -*- coding: utf-8 -*-
import collections
import re

import py
import pytest


@pytest.fixture
def tmp_tree_of_tests(testdir):
    """
    Creates a directory structure:
        tmpdir/
            shallow_tests/
                test_a.py 2 passing, 1 failing
                deep_tests/
                    test_b.py 2 passing, 1 failing
                    test_c.py 1 passing
                    test_d.py 2 passing
                    test_e.py a class, 2 passing, 1 failing

    If module name doesn't start with "test_", it isn't picked up by runpytest.
    """

    sup = testdir.mkpydir('shallow_tests')

    sup.join('test_a.py').write(py.code.Source("""
        def test_a1():
            assert False
        def test_a2():
            assert True
        def test_a3():
            assert True
    """))

    sup.join('test_ax.py').write(py.code.Source("""
        def test_ax1():
            assert True
        def test_ax2():
            assert True
        def test_ax3():
            assert True
    """))

    sub = testdir.mkpydir('shallow_tests/deep_tests')

    sub.join('test_b.py').write(py.code.Source("""
        def test_b1():
            assert True
        def test_b2():
            assert False
        def test_b3():
            assert True
    """))

    sub.join('test_c.py').write(py.code.Source("""
        def test_c1():
            assert True
    """))

    sub.join('test_d.py').write(py.code.Source("""
        def test_d1():
            assert True
        def test_d2():
            assert True
    """))

    sub.join('test_e.py').write(py.code.Source("""
        from unittest import TestCase
        class EeTest(TestCase):
            def test_ee1(self):
                self.assertTrue(True)
            def test_ee2(self):
                self.assertFalse(True)
            def test_ee3(self):
                self.assertTrue(True)

        class ExTest(TestCase):
            def test_ex1(self):
                self.assertTrue(True)
            def test_ex2(self):
                self.assertTrue(True)
    """))

    return testdir


def check_call_sequence(seq, bucket='module'):
    all_values = collections.defaultdict(list)
    num_switches = collections.defaultdict(int)

    def inspect_attr(this_call, prev_call, attr_name):
        attr_value = getattr(this_call, attr_name)
        prev_value = getattr(prev_call, attr_name) if prev_call else -1
        all_values[attr_name].append(attr_value)
        if attr_value != prev_value:
            num_switches[attr_name] += 1

    for i, this_call in enumerate(seq):
        prev_call = seq[i - 1] if i > 0 else None
        inspect_attr(this_call, prev_call, 'package')
        inspect_attr(this_call, prev_call, 'module')
        inspect_attr(this_call, prev_call, 'cls')

    num_packages = len(set(all_values['package']))
    num_package_switches = num_switches['package']
    num_modules = len(set(all_values['module']))
    num_module_switches = num_switches['module']
    num_classes = len(set(all_values['class']))
    num_class_switches = num_switches['class']

    # These are just sanity tests, the actual shuffling is tested in test_shuffle,
    # assertions here are very relaxed.

    if bucket == 'global':
        if num_module_switches <= num_modules:
            pytest.fail('Too few module switches for global shuffling')
        if num_package_switches <= num_packages:
            pytest.fail('Too few package switches for global shuffling')

    elif bucket == 'package':
        assert num_package_switches == num_packages
        if num_module_switches <= num_modules:
            pytest.fail('Too few module switches for package-limited shuffling')

    elif bucket == 'module':
        assert num_module_switches == num_modules

    elif bucket == 'class':
        # Each class can contribute to 1 or 2 switches.
        assert num_class_switches <= num_classes * 2

        # Class bucket is a special case of module bucket.
        # We have two classes in one module and these could be reshuffled so
        # the module could appear in sequence of buckets two times.
        assert num_modules <= num_module_switches <= num_modules + 1


@pytest.mark.parametrize('bucket,min_sequences,max_sequences', [
    ('class', 2, 5),
    ('module', 2, 5),
    ('package', 2, 5),
    ('global', 2, 5),
    ('none', 1, 1),
    ('parent', 1, 5),
    ('grandparent', 1, 5),
])
def test_it_works_with_actual_tests(tmp_tree_of_tests, get_test_calls, bucket, min_sequences, max_sequences):
    sequences = set()

    for x in range(5):
        result = tmp_tree_of_tests.runpytest('--random-order-bucket={0}'.format(bucket), '--verbose')
        result.assert_outcomes(passed=14, failed=3)
        seq = get_test_calls(result)
        check_call_sequence(seq, bucket=bucket)
        assert len(seq) == 17
        sequences.add(seq)

    assert min_sequences <= len(sequences) <= max_sequences


def test_random_order_seed_is_respected(testdir, twenty_tests, get_test_calls):
    testdir.makepyfile(twenty_tests)
    call_sequences = {
        '1': None,
        '2': None,
        '3': None,
    }
    for seed in call_sequences.keys():
        result = testdir.runpytest('--random-order-seed={0}'.format(seed))

        result.stdout.fnmatch_lines([
            '*Using --random-order-seed={0}*'.format(seed),
        ])

        result.assert_outcomes(passed=20)
        call_sequences[seed] = get_test_calls(result)

    for seed in call_sequences.keys():
        result = testdir.runpytest('--random-order-seed={0}'.format(seed))
        result.assert_outcomes(passed=20)
        assert call_sequences[seed] == get_test_calls(result)

    assert call_sequences['1'] != call_sequences['2'] != call_sequences['3']


def test_generated_seed_is_reported_and_run_can_be_reproduced(testdir, twenty_tests, get_test_calls):
    testdir.makepyfile(twenty_tests)
    result = testdir.runpytest('-v', '--random-order')
    result.assert_outcomes(passed=20)
    result.stdout.fnmatch_lines([
        '*Using --random-order-seed=*'
    ])
    calls = get_test_calls(result)

    # find the seed in output
    seed = None
    for line in result.outlines:
        g = re.match('^Using --random-order-seed=(.+)$', line)
        if g:
            seed = g.group(1)
            break
    assert seed

    result2 = testdir.runpytest('-v', '--random-order-seed={0}'.format(seed))
    result2.assert_outcomes(passed=20)
    calls2 = get_test_calls(result2)
    assert calls == calls2


@pytest.mark.parametrize('bucket', [
    'global',
    'package',
    'module',
    'class',
    'parent',
    'grandparent',
    'none',
])
def test_failed_first(tmp_tree_of_tests, get_test_calls, bucket):
    result1 = tmp_tree_of_tests.runpytest('--random-order-bucket={0}'.format(bucket), '--verbose')
    result1.assert_outcomes(passed=14, failed=3)

    result2 = tmp_tree_of_tests.runpytest('--random-order-bucket={0}'.format(bucket), '--failed-first', '--verbose')
    result2.assert_outcomes(passed=14, failed=3)

    calls2 = get_test_calls(result2)
    first_three_tests = set(c.name for c in calls2[:3])
    assert set(['test_a1', 'test_b2', 'test_ee2']) == first_three_tests
