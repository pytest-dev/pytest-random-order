# -*- coding: utf-8 -*-

import random
import sys
import traceback


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


_random_order_item_keys = {
    'global': lambda x: None,
    'package': lambda x: x.module.__package__,
    'module': lambda x: x.module.__name__,
    'class': lambda x: (x.module.__name__, x.cls.__name__) if x.cls else x.module.__name__,
}


def _shuffle_items(items, key=None, preserve_bucket_order=False):
    """
    Shuffles `items`, a list, in place.

    If `key` is None, items are shuffled across the entire list.

    Otherwise `key` is a function called for each item in `items` to
    calculate key of bucket in which the item falls.

    Bucket defines the boundaries across which tests will not
    be reordered.

    `preserve_bucket_order` is only customisable for testing purposes.
    There is no use case for predefined bucket order, is there?
    """

    # If `key` is falsey, shuffle is global.
    if not key:
        random.shuffle(items)
        return

    buckets = []
    this_key = '__not_initialised__'
    for item in items:
        prev_key = this_key
        this_key = key(item)
        if this_key != prev_key:
            buckets.append([])
        buckets[-1].append(item)

    # Shuffle within bucket
    for bucket in buckets:
        random.shuffle(bucket)

    # Shuffle buckets
    if not preserve_bucket_order:
        random.shuffle(buckets)

    items[:] = [item for bucket in buckets for item in bucket]
    return


def _get_set_of_item_ids(items):
    s = {}
    try:
        s = set(item.nodeid for item in items)
    finally:
        return s


def pytest_collection_modifyitems(session, config, items):
    failure = None
    item_ids = _get_set_of_item_ids(items)

    try:
        shuffle_mode = config.getoption('random_order_bucket')
        _shuffle_items(items, key=_random_order_item_keys[shuffle_mode])

    except Exception as e:
        # If the number of items is still the same, we assume that we haven't messed up too hard
        # and we can just return the list of items as it is.
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
