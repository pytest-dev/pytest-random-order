import collections

import pytest


pytest_plugins = 'pytester'


Call = collections.namedtuple('Call', field_names=('package', 'module', 'cls', 'name'))


def _get_test_calls(result):
    """
    Returns a tuple of test calls in the order they were made.
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
def get_test_calls():
    """
    Returns a function to get runtest calls out from testdir.pytestrun result object.
    """
    return _get_test_calls
