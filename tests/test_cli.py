def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    result.stdout.fnmatch_lines([
        'pytest-random-order options:',
        '*--random-order-bucket={global,package,module,class,parent,grandparent,none}*',
        '*--random-order-seed=*',
    ])


def test_markers_message(testdir):
    result = testdir.runpytest(
        '--markers',
    )
    result.stdout.fnmatch_lines([
        '*@pytest.mark.random_order(disabled=True): disable reordering*',
    ])
