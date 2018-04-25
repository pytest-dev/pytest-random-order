import random
import sys
import traceback

from pytest_random_order.shuffler import _get_set_of_item_ids, _shuffle_items, _disable


def pytest_addoption(parser):
    group = parser.getgroup('random-order')
    group.addoption(
        '--random-order-bucket',
        action='store',
        dest='random_order_bucket',
        default='module',
        choices=('global', 'package', 'module', 'class', 'parent', 'grandparent', 'none'),
        help='Limit reordering of test items across units of code',
    )
    group.addoption(
        '--random-order-seed',
        action='store',
        dest='random_order_seed',
        default=str(random.randint(1, 1000000)),
        help='Seed for the test order randomiser to produce a random order that can be reproduced using this seed',
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "random_order(disabled=True): disable reordering of tests within a module or class")


def pytest_report_header(config):
    out = ''

    if config.getoption('random_order_bucket'):
        out += "Using --random-order-bucket={0}\n".format(config.getoption('random_order_bucket'))

    if config.getoption('random_order_seed'):
        out += 'Using --random-order-seed={0}\n'.format(config.getoption('random_order_seed'))

    return out


def pytest_collection_modifyitems(session, config, items):
    failure = None

    item_ids = _get_set_of_item_ids(items)

    try:
        seed = str(config.getoption('random_order_seed'))
        bucket_type = config.getoption('random_order_bucket')
        if bucket_type != 'none':
            _shuffle_items(items, bucket_key=_random_order_item_keys[bucket_type], disable=_disable, seed=seed)

    except Exception as e:
        # See the finally block -- we only fail if we have lost user's tests.
        _, _, exc_tb = sys.exc_info()
        failure = 'pytest-random-order plugin has failed with {0!r}:\n{1}'.format(
            e, ''.join(traceback.format_tb(exc_tb, 10))
        )
        config.warn(0, failure, None)

    finally:
        # Fail only if we have lost user's tests
        if item_ids != _get_set_of_item_ids(items):
            if not failure:
                failure = 'pytest-random-order plugin has failed miserably'
            raise RuntimeError(failure)


_random_order_item_keys = {
    'global': lambda x: None,
    'package': lambda x: x.module.__package__,
    'module': lambda x: x.module.__name__,
    'class': lambda x: (x.module.__name__, x.cls.__name__) if x.cls else x.module.__name__,
    'parent': lambda x: x.parent,
    'grandparent': lambda x: x.parent.parent,
}
