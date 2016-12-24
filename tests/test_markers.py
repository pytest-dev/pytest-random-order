import pytest


@pytest.fixture
def twenty_tests():
    code = []
    for i in range(20):
        code.append('def test_a{}(): assert True\n'.format(str(i).zfill(2)))
    return ''.join(code)


@pytest.mark.parametrize('disabled', [True])
def test_pytest_mark_random_order_disabled(testdir, twenty_tests, get_test_calls, disabled):
    testdir.makepyfile(
        'import pytest\n' +
        'pytest.mark.random_order_disabled = {}\n'.format(disabled) +
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
