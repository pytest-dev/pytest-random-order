# -*- coding: utf-8 -*-
import collections

import py
import pytest


Call = collections.namedtuple('Call', field_names=('package', 'module', 'cls', 'name'))


def get_runtest_call_sequence(result, key=None):
    """
    Returns a tuple of names of test methods that were run
    in the order they were run.
    """
    calls = []

    for c in result.reprec.getcalls('pytest_runtest_call'):
        calls.append(Call(
            package=c.item.module.__package__,
            module=c.item.module.__name__,
            cls=(c.item.module.__name__, c.item.cls.__name__) if c.item.cls else None,
            name=c.item.name,
        ))
    return tuple(calls)


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


def check_call_sequence(seq, shuffle_mode='module'):
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

    if shuffle_mode == 'global':
        if num_module_switches <= num_modules:
            pytest.fail('Too few module switches for global shuffling')
        if num_package_switches <= num_packages:
            pytest.fail('Too few package switches for global shuffling')

    elif shuffle_mode == 'package':
        assert num_package_switches == num_packages
        if num_module_switches <= num_modules:
            pytest.fail('Too few module switches for package-limited shuffling')

    elif shuffle_mode == 'module':
        assert num_module_switches == num_modules

    elif shuffle_mode == 'cls':
        # Each class can contribute to 1 or 2 switches.
        assert num_class_switches <= num_classes * 2

        # Class shuffle is a subset of module shuffle
        assert num_module_switches == num_modules


@pytest.mark.parametrize('mode', ['class', 'module', 'package', 'global'])
def test_it_works_with_actual_tests(tmp_tree_of_tests, mode):
    sequences = set()

    for x in range(5):
        result = tmp_tree_of_tests.runpytest('--random-order-mode={}'.format(mode), '--verbose')
        result.assert_outcomes(passed=14, failed=3)
        seq = get_runtest_call_sequence(result)
        check_call_sequence(seq, shuffle_mode=mode)
        assert len(seq) == 17
        sequences.add(seq)

    assert 1 < len(sequences) <= 5
