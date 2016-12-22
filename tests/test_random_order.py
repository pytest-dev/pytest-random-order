# -*- coding: utf-8 -*-
import py
import pytest


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    result.stdout.fnmatch_lines([
        'random-order:',
        # '*--random-order-seed=RANDOM_ORDER_SEED*',
        '*--random-order-mode={global,package,module}*',
    ])


def get_runtest_call_sequence(result, key=None):
    """
    Returns a tuple of names of test methods that were run
    in the order they were run.
    """
    calls = []

    for c in result.reprec.getcalls('pytest_runtest_call'):
        calls.append((c.item.module.__package__, c.item.module.__name__, c.item.name))
    return tuple(calls)


@pytest.fixture
def tmp_tree_of_tests(testdir):
    """
    Creates a directory structure:
        tmpdir/
            shallow_tests/
                test_a.py
                deep_tests/
                    test_b.py
                    test_c.py

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

    return testdir


def check_call_sequence(seq, shuffle_mode='module'):
    packages_seen = []
    modules_seen = []

    num_package_switches = 0
    num_module_switches = 0

    for package, module, item in seq:
        if not packages_seen:
            num_package_switches += 1
            packages_seen.append(package)
        elif packages_seen[-1] == package:
            # Same package as the previous item
            pass
        else:
            num_package_switches += 1
            if package not in packages_seen:
                packages_seen.append(package)

        if not modules_seen:
            num_module_switches += 1
            modules_seen.append(module)
        elif modules_seen[-1] == module:
            # Same module as the previous item
            pass
        else:
            num_module_switches += 1
            if module not in modules_seen:
                modules_seen.append(module)

    if shuffle_mode == 'global':
        if len(packages_seen) >= num_package_switches:
            pytest.fail(
                'Too few package switches ({}) for '
                'random-shuffle-mode=global. Packages seen: {}'.format(
                    num_package_switches,
                    packages_seen,
                )
            )

    if shuffle_mode == 'package':
        if len(packages_seen) != num_package_switches:
            pytest.fail('There were more package switches than number of packages')

        if len(modules_seen) >= num_module_switches:
            pytest.fail(
                'Suspiciously few module switches ({}) for '
                'random-shuffle-mode=package. Modules seen: {}'.format(
                    num_module_switches,
                    modules_seen,
                )
            )

    elif shuffle_mode == 'module' and len(modules_seen) != num_module_switches:
        pytest.fail('There were more module switches than number of modules')


@pytest.mark.parametrize('mode', ['module', 'package', 'global'])
def test_it_works(tmp_tree_of_tests, mode):
    sequences = set()

    for x in xrange(5):
        result = tmp_tree_of_tests.runpytest('--random-order-mode={}'.format(mode), '--verbose')
        result.assert_outcomes(passed=10, failed=2)
        seq = get_runtest_call_sequence(result)
        check_call_sequence(seq, shuffle_mode=mode)
        assert len(seq) == 12
        sequences.add(seq)

    assert 1 < len(sequences) <= 5
