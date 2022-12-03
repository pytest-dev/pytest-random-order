
def test_xdist_not_broken(testdir, twenty_tests):
    testdir.makepyfile(twenty_tests)

    result = testdir.runpytest('--random-order', '-n', '5')
    result.assert_outcomes(passed=20)
