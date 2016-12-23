def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    result.stdout.fnmatch_lines([
        'random-order:',
        '*--random-order-bucket={global,package,module,class}*',
    ])
