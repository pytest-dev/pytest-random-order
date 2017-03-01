def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    result.stdout.fnmatch_lines([
        'random-order:',
        '*--random-order-enable*',
        '*--random-order-bucket={global,package,module,class}*',
        '*--random-order-seed=*',
    ])


def test_markers_message(testdir):
    result = testdir.runpytest(
        '--markers',
    )
    result.stdout.fnmatch_lines([
        '*@pytest.mark.random_order(disabled=True): disable reordering*',
    ])
