import collections

import pytest

pytest_plugins = "pytester"


Call = collections.namedtuple("Call", field_names=("package", "module", "cls", "name"))


def _get_test_calls(result):
    """
    Returns a tuple of test calls in the order they were made.
    """
    calls = []

    for c in result.reprec.getcalls("pytest_runtest_call"):
        calls.append(
            Call(
                package=c.item.module.__package__,
                module=c.item.module.__name__,
                cls=(c.item.module.__name__, c.item.cls.__name__) if c.item.cls else None,
                name=c.item.name,
            )
        )
    return tuple(calls)


@pytest.fixture
def get_test_calls():
    """
    Returns a function to get runtest calls out from testdir.pytestrun result object.
    """
    return _get_test_calls


@pytest.fixture
def twenty_tests():
    code = []
    for i in range(20):
        code.append("def test_a{0}(): assert True\n".format(str(i).zfill(2)))
    return "".join(code)


@pytest.fixture
def twenty_cls_tests():
    code = []
    for i in range(20):
        code.append("\tdef test_b{0}(self): self.assertTrue\n".format(str(i).zfill(2)))
    return "".join(code)


def _deindent_source(source):
    """
    A minimal replacement for py.code.Source to deindent inlined test code.
    Looks for the first non-empty line to determine deindent offset, doesn't
    attempt to understand the code, line continuations, etc.
    """
    lines = source.splitlines()
    for line in lines:
        stripped = line.lstrip()
        if stripped:
            offset = len(line) - len(stripped)
            break
    else:
        offset = 0

    output_lines = []
    for line in lines:
        output_lines.append(line[offset:])

    return "\n".join(output_lines)


@pytest.fixture
def deindent_source():
    """
    Returns a helper function to deindent inlined source code.
    """
    return _deindent_source
