# -*- coding: utf-8 -*-

import collections
import operator
import random


"""
`bucket` is a string representing the bucket in which the item falls based on user's chosen
bucket type.

`disabled` is either a falsey value to mark that the item is ready for shuffling (shuffling is not disabled),
or a truthy value in which case the item won't be shuffled among other items with the same key.

In some cases it is important for the `disabled` to be more than just True in order
to preserve a distinct disabled sub-bucket within a larger bucket and not mix it up with another
disabled sub-bucket of the same larger bucket.
"""
ItemKey = collections.namedtuple('ItemKey', field_names=('bucket', 'disabled', 'x'))
ItemKey.__new__.__defaults__ = (None, None)


def _shuffle_items(items, bucket_key=None, disable=None, _shuffle_buckets=True):
    """
    Shuffles a list of `items` in place.

    If `bucket_key` is None, items are shuffled across the entire list.

    `bucket_key` is an optional function called for each item in `items` to
    calculate the key of bucket in which the item falls.

    Bucket defines the boundaries across which items will not
    be shuffled.

    If `disable` is function and returns True for ALL items
    in a bucket, items in this bucket will remain in their original order.

    `_shuffle_buckets` is for testing only. Setting it to False may not produce
    the outcome you'd expect in all scenarios because if two non-contiguous sections of items belong
    to the same bucket, the items in these sections will be reshuffled as if they all belonged
    to the first section.
        Example:
            [A1, A2, B1, B2, A3, A4]

            where letter denotes bucket key,
            with _shuffle_buckets=False may be reshuffled to:
                [B2, B1, A3, A1, A4, A2]

            or as well to:
                [A3, A2, A4, A1, B1, B2]

            because all A's belong to the same bucket and will be grouped together.
    """

    # If `bucket_key` is falsey, shuffle is global.
    if not bucket_key and not disable:
        random.shuffle(items)
        return

    def get_full_bucket_key(item):
        assert bucket_key or disable
        if bucket_key and disable:
            return ItemKey(bucket=bucket_key(item), disabled=disable(item))
        elif disable:
            return ItemKey(disabled=disable(item))
        else:
            return ItemKey(bucket=bucket_key(item))

    # For a sequence of items A1, A2, B1, B2, C1, C2,
    # where key(A1) == key(A2) == key(C1) == key(C2),
    # items A1, A2, C1, and C2 will end up in the same bucket.
    buckets = collections.OrderedDict()
    for item in items:
        full_bucket_key = get_full_bucket_key(item)
        if full_bucket_key not in buckets:
            buckets[full_bucket_key] = []
        buckets[full_bucket_key].append(item)

    # Shuffle inside a bucket
    for bucket in buckets.keys():
        if not bucket.disabled:
            random.shuffle(buckets[bucket])

    # Shuffle buckets
    bucket_keys = list(buckets.keys())
    random.shuffle(bucket_keys)

    items[:] = [item for bk in bucket_keys for item in buckets[bk]]
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
        # In actual test runs, this is returned as a truthy instance of MarkDecorator even when you don't have
        # set the marker. This is a hack.
        is_disabled = _is_random_order_disabled(item.module)
        if is_disabled and is_disabled is True:
            # It is not enough to return just True because in case the shuffling
            # is disabled on module, we must preserve the module unchanged
            # even when the bucket type for this test run is say package or global.
            return item.module.__name__
    except AttributeError:
        pass
    return False
