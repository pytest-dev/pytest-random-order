# -*- coding: utf-8 -*-

import random
import sys
import traceback

import operator


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


def _shuffle_items(items, key=None, disable=None, preserve_bucket_order=False):
    """
    Shuffles `items`, a list, in place.

    If `key` is None, items are shuffled across the entire list.

    Otherwise `key` is a function called for each item in `items` to
    calculate key of bucket in which the item falls.

    Bucket defines the boundaries across which tests will not
    be reordered.

    If `disable` is function and returns True for ALL items
    in a bucket, items in this bucket will remain in their original order.

    `preserve_bucket_order` is only customisable for testing purposes.
    There is no use case for predefined bucket order, is there?
    """

    # If `key` is falsey, shuffle is global.
    if not key and not disable:
        random.shuffle(items)
        return

    # Use (key(x), disable(x)) as the key because
    # when we have a bucket type like package over a disabled module, we must
    # not shuffle the disabled module items.
    def full_key(x):
        if key and disable:
            return key(x), disable(x)
        elif disable:
            return disable(x)
        else:
            return key(x)

    buckets = []
    this_key = '__not_initialised__'
    for item in items:
        prev_key = this_key
        this_key = full_key(item)
        if this_key != prev_key:
            buckets.append([])
        buckets[-1].append(item)

    # Shuffle within bucket unless disable(item) evaluates to True for
    # the first item in the bucket.
    # This assumes that whoever supplied disable function knows this requirement.
    # Fixation of individual items in an otherwise shuffled bucket
    # is not supported.
    for bucket in buckets:
        if callable(disable) and disable(bucket[0]):
            continue
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


_is_random_order_disabled = operator.attrgetter('pytest.mark.random_order_disabled')


def _disable(item):
    try:
        if _is_random_order_disabled(item.module):
            # It is not enough to return just True because in case the shuffling
            # is disabled on module, we must preserve the module unchanged
            # even when the bucket type for this test run is say package or global.
            return item.module.__name__
    except AttributeError:
        return False


def pytest_collection_modifyitems(session, config, items):
    failure = None

    item_ids = _get_set_of_item_ids(items)

    try:
        bucket_type = config.getoption('random_order_bucket')
        _shuffle_items(items, key=_random_order_item_keys[bucket_type], disable=_disable)

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
