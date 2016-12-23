# -*- coding: utf-8 -*-

import random


def pytest_addoption(parser):
    group = parser.getgroup('random-order')
    group.addoption(
        '--random-order-mode',
        action='store',
        dest='random_order_mode',
        default='module',
        choices=('global', 'package', 'module', 'class'),
        help='Limit reordering of test items across units of code',
    )


def pytest_report_header(config):
    out = None

    if config.getoption('random_order_mode'):
        mode = config.getoption('random_order_mode')
        out = "Using --random-order-mode={0}".format(mode)

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


def pytest_collection_modifyitems(session, config, items):
    shuffle_mode = config.getoption('random_order_mode')
    _shuffle_items(items, key=_random_order_item_keys[shuffle_mode])
