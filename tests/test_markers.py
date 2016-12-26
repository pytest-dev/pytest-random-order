import pytest


@pytest.fixture
def twenty_tests():
    code = []
    for i in range(20):
        code.append('def test_a{}(): assert True\n'.format(str(i).zfill(2)))
    return ''.join(code)


@pytest.fixture
def twenty_cls_tests():
    code = []
    for i in range(20):
        code.append('\tdef test_b{}(self): self.assertTrue\n'.format(str(i).zfill(2)))
    return ''.join(code)


@pytest.mark.parametrize('disabled', [True, False])
def test_marker_disables_random_order_in_module(testdir, twenty_tests, get_test_calls, disabled):
    testdir.makepyfile(
        'import pytest\n' +
        ('pytestmark = pytest.mark.random_order(disabled={})\n'.format(disabled)) +
        twenty_tests
    )

    result = testdir.runpytest('--random-order-bucket=module', '-v')
    result.assert_outcomes(passed=20)
    names = [c.name for c in get_test_calls(testdir.runpytest())]
    sorted_names = sorted(list(names))

    if disabled:
        assert names == sorted_names
    else:
        assert names != sorted_names


@pytest.mark.parametrize('disabled', [True, False])
def test_marker_disables_random_order_in_class(testdir, twenty_cls_tests, get_test_calls, disabled):
    testdir.makepyfile(
        'import pytest\n\n' +
        'from unittest import TestCase\n\n' +
        'class MyTest(TestCase):\n' +
        '\tpytestmark = pytest.mark.random_order(disabled={})\n'.format(disabled) +
        twenty_cls_tests + '\n'
    )

    result = testdir.runpytest('--random-order-bucket=module', '-v')
    result.assert_outcomes(passed=20)
    names = [c.name for c in get_test_calls(testdir.runpytest())]
    sorted_names = sorted(list(names))

    if disabled:
        assert names == sorted_names
    else:
        assert names != sorted_names
