import pytest


def acceptably_failing_shuffle_items(items, **kwargs):
    # Does not mess up items collection
    raise ValueError('shuffling failed')


def critically_failing_shuffle_items(items, **kwargs):
    # Messes up items collection, an item is effectively lost
    items[1] = items[0]
    raise ValueError('shuffling failed')


def critically_not_failing_shuffle_items(items, **kwargs):
    # This shuffler doesn't raise an exception but it does lose test cases
    items[1] = items[0]


@pytest.fixture
def simple_testdir(testdir):
    testdir.makepyfile("""
        def test_a1():
            assert True

        def test_a2():
            assert True
    """)
    return testdir


def test_faulty_shuffle_that_preserves_items_does_not_fail_test_run(monkeypatch, simple_testdir):
    monkeypatch.setattr('random_order.plugin._shuffle_items', acceptably_failing_shuffle_items)

    result = simple_testdir.runpytest('--random-order')
    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines("""
        *pytest-random-order plugin has failed with ValueError*
    """)


def test_faulty_shuffle_that_loses_items_fails_test_run(monkeypatch, simple_testdir):
    monkeypatch.setattr('random_order.plugin._shuffle_items', critically_failing_shuffle_items)
    result = simple_testdir.runpytest('--random-order')
    result.assert_outcomes(passed=0, failed=0, skipped=0)
    result.stdout.fnmatch_lines("""
        *INTERNALERROR> RuntimeError: pytest-random-order plugin has failed with ValueError*
    """)


def test_seemingly_ok_shuffle_that_loses_items_fails_test_run(monkeypatch, simple_testdir):
    monkeypatch.setattr('random_order.plugin._shuffle_items', critically_not_failing_shuffle_items)
    result = simple_testdir.runpytest('--random-order')
    result.assert_outcomes(passed=0, failed=0, skipped=0)
    result.stdout.fnmatch_lines("""
        *INTERNALERROR> RuntimeError: pytest-random-order plugin has failed miserably*
    """)
