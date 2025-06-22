import pytest

from random_order.shuffler import _shuffle_items


def identity_key(item, session):
    return item


def modulus_2_key(item, session):
    return item % 2


def lt_10_key(item, session):
    return item < 10


def disable_if_gt_1000(item, session):
    # if disable returns a truthy value, it must also be usable as a key.
    if item > 1000:
        return item // 1000
    else:
        return False


@pytest.mark.parametrize(
    "key",
    [
        None,
        lambda item, session: None,
        lambda item, session: item % 2,
    ],
)
def test_shuffles_empty_list_in_place(key):
    items = []
    items_id = id(items)
    _shuffle_items(items, bucket_key=key)
    assert items == []
    assert id(items) == items_id


@pytest.mark.parametrize(
    "key",
    [
        None,
        lambda item, session: None,
        lambda item, session: item % 2,
    ],
)
def test_shuffles_one_item_list_in_place(key):
    items = [42]
    items_id = id(items)
    _shuffle_items(items, bucket_key=key)
    assert items == [42]
    assert id(items) == items_id


def test_identity_key_results_in_complete_reshuffle():
    items = list(range(20))
    items_copy = list(items)
    _shuffle_items(items, bucket_key=identity_key)
    assert items != items_copy


def test_two_bucket_reshuffle():
    # If we separate a list of 20 integers from 0 to 19 into two buckets
    # [[0..9], [10..19]] then the result should be
    # either [{0..9}, {10..19}]
    # or [{10..19}, {0..9}]
    items = list(range(20))
    items_copy = list(items)
    _shuffle_items(items, bucket_key=lt_10_key)
    assert items != items_copy
    for i, item in enumerate(items):
        if lt_10_key(i, None):
            assert lt_10_key(item, None) == lt_10_key(items[0], None), items
        else:
            assert lt_10_key(item, None) == lt_10_key(items[10], None), items


def test_eight_bucket_reshuffle():
    # This is a cross-check to test shuffling of buckets.
    items = [
        1,
        1,
        2,
        2,
        3,
        3,
        4,
        4,
        5,
        5,
        6,
        6,
        7,
        7,
        8,
        8,
    ]
    items_copy = list(items)

    _shuffle_items(items, bucket_key=identity_key)

    assert items != items_copy

    # Items of the same bucket should remain next to each other.
    assert items[0] == items[1]
    assert items[2] == items[3]
    assert items[-1] == items[-2]


def test_shuffle_respects_single_disabled_group_in_each_of_two_buckets():
    items = [
        11,
        13,
        9995,
        9997,
        19,
        21,
        23,
        25,
        27,
        29,  # bucket 1 -- odd numbers
        12,
        14,
        9996,
        9998,
        20,
        22,
        24,
        26,
        28,
        30,  # bucket 2 -- even numbers
    ]
    items_copy = list(items)

    _shuffle_items(items, bucket_key=modulus_2_key, disable=disable_if_gt_1000)

    assert items != items_copy
    assert items.index(9995) + 1 == items.index(9997)
    assert items.index(9996) + 1 == items.index(9998)


def test_shuffle_respects_two_distinct_disabled_groups_in_one_bucket():
    # all items are in one oddity bucket, but the two groups
    # of large numbers are separate because they are disabled
    # from two different units.
    # This is simulating two disabled modules within same package.
    # The two modules shouldn't be mixed up in one bucket.
    items = [
        11,
        13,
        8885,
        8887,
        8889,
        21,
        23,
        9995,
        9997,
        9999,
    ]
    items_copy = list(items)

    for i in range(5):
        _shuffle_items(items, bucket_key=modulus_2_key, disable=disable_if_gt_1000)
        if items != items_copy:
            assert items[items.index(8885) : items.index(8885) + 3] == [8885, 8887, 8889]
            assert items[items.index(9995) : items.index(9995) + 3] == [9995, 9997, 9999]
            return

    assert False


def test_shuffle_respects_seed():
    sorted_items = list(range(30))

    for seed in range(20):
        # Reset
        items1 = list(range(30))
        _shuffle_items(items1, seed=seed)

        assert items1 != sorted_items

        items2 = list(range(30))
        _shuffle_items(items2, seed=seed)

        assert items2 == items1
