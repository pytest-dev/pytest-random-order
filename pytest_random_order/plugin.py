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
        choices=('global', 'package', 'module', 'class'),
        help='Limit reordering of test items across units of code',
    )


def pytest_report_header(config):
    out = None

    if config.getoption('random_order_bucket'):
        bucket = config.getoption('random_order_bucket')
        out = "Using --random-order-bucket={0}".format(bucket)

    return out


def pytest_collection_modifyitems(session, config, items):
    failure = None

    item_ids = _get_set_of_item_ids(items)

    try:
        bucket_type = config.getoption('random_order_bucket')
        _shuffle_items(items, bucket_key=_random_order_item_keys[bucket_type], disable=_disable)

    except Exception as e:
        # See the finally block -- we only fail if we have lost user's tests.
        _, _, exc_tb = sys.exc_info()
        failure = 'pytest-random-order plugin has failed with {!r}:\n{}'.format(
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
}
