# -*- coding: utf-8 -*-

import random
from collections import OrderedDict, namedtuple

from random_order.cache import FAILED_FIRST_LAST_FAILED_BUCKET_KEY

"""
`bucket` is a string representing the bucket in which the item falls based on user's chosen
bucket type.

`disabled` is either a falsey value to mark that the item is ready for shuffling (shuffling is not disabled),
or a truthy value in which case the item won't be shuffled among other items with the same key.

In some cases it is important for the `disabled` to be more than just True in order
to preserve a distinct disabled sub-bucket within a larger bucket and not mix it up with another
disabled sub-bucket of the same larger bucket.
"""
ItemKey = namedtuple('ItemKey', field_names=('bucket', 'disabled', 'x'))
ItemKey.__new__.__defaults__ = (None, None)


def _shuffle_items(items, bucket_key=None, disable=None, seed=None, session=None):
    """
    Shuffles a list of `items` in place.

    If `bucket_key` is None, items are shuffled across the entire list.

    `bucket_key` is an optional function called for each item in `items` to
    calculate the key of bucket in which the item falls.

    Bucket defines the boundaries across which items will not
    be shuffled.

    `disable` is a function that takes an item and returns a falsey value
    if this item is ok to be shuffled. It returns a truthy value otherwise and
    the truthy value is used as part of the item's key when determining the bucket
    it belongs to.
    """

    if seed is not None:
        random.seed(seed)

    # If `bucket_key` is falsey, shuffle is global.
    if not bucket_key and not disable:
        random.shuffle(items)
        return

    def get_full_bucket_key(item):
        assert bucket_key or disable
        if bucket_key and disable:
            return ItemKey(bucket=bucket_key(item, session), disabled=disable(item, session))
        elif disable:
            return ItemKey(disabled=disable(item, session))
        else:
            return ItemKey(bucket=bucket_key(item, session))

    # For a sequence of items A1, A2, B1, B2, C1, C2,
    # where key(A1) == key(A2) == key(C1) == key(C2),
    # items A1, A2, C1, and C2 will end up in the same bucket.
    buckets = OrderedDict()
    for item in items:
        full_bucket_key = get_full_bucket_key(item)
        if full_bucket_key not in buckets:
            buckets[full_bucket_key] = []
        buckets[full_bucket_key].append(item)

    # Shuffle inside a bucket

    bucket_keys = list(buckets.keys())

    for full_bucket_key in buckets.keys():
        if full_bucket_key.bucket == FAILED_FIRST_LAST_FAILED_BUCKET_KEY:
            # Do not shuffle the last failed bucket
            continue

        if not full_bucket_key.disabled:
            random.shuffle(buckets[full_bucket_key])

    # Shuffle buckets

    # Only the first bucket can be FAILED_FIRST_LAST_FAILED_BUCKET_KEY
    if bucket_keys and bucket_keys[0].bucket == FAILED_FIRST_LAST_FAILED_BUCKET_KEY:
        new_bucket_keys = list(buckets.keys())[1:]
        random.shuffle(new_bucket_keys)
        new_bucket_keys.insert(0, bucket_keys[0])
    else:
        new_bucket_keys = list(buckets.keys())
        random.shuffle(new_bucket_keys)

    items[:] = [item for bk in new_bucket_keys for item in buckets[bk]]
    return


def _get_set_of_item_ids(items):
    s = {}
    try:
        s = set(item.nodeid for item in items)
    finally:
        return s


def _disable(item, session):
    if hasattr(item, 'get_closest_marker'):
        marker = item.get_closest_marker('random_order')
    else:
        marker = item.get_marker('random_order')
    if marker:
        is_disabled = marker.kwargs.get('disabled', False)
        if is_disabled:
            # A test item can only be disabled in its parent context -- where it is part of some order.
            # We use parent name as the key so that all children of the same parent get the same disabled key.
            return item.parent.name
    return False
