import pytest


from pytest_random_order import _shuffle_items


def identity_key(x):
    return x


def oddity_key(x):
    return x % 2


@pytest.mark.parametrize('key', [
    None,
    lambda x: None,
    lambda x: x % 2,
])
def test_shuffles_empty_list_in_place(key):
    items = []
    items_id = id(items)
    _shuffle_items(items, key=key)
    assert items == []
    assert id(items) == items_id


@pytest.mark.parametrize('key', [
    None,
    lambda x: None,
    lambda x: x % 2,
])
def test_shuffles_one_item_list_in_place(key):
    items = [42]
    items_id = id(items)
    _shuffle_items(items, key=key)
    assert items == [42]
    assert id(items) == items_id


def test_shuffle_respects_bucket_order():
    # In this test, it does not matter that multiple buckets have the same key
    # because we are running _shuffle_items with preserve_bucket_order=True.
    # Shuffling will happen only within a bucket (items with the same key).
    items = [
        1, 3, 5, 7,         # oddity_key(item) = 1
        2, 4, 6,            # 0
        9, 11, 13, 15, 17,  # 1
        8,                  # 0
        19, 21,             # 1
        10,                 # 0
    ]
    items_copy = list(items)

    # No shuffling because identity_key returns a unique key for our distinct items
    _shuffle_items(items, key=identity_key, preserve_bucket_order=True)
    assert items == items_copy

    # Should leave buckets in their relative order.
    # Single item buckets should remain unchanged.
    for x in range(3):
        _shuffle_items(items, key=oddity_key, preserve_bucket_order=True)
        assert items != items_copy
        assert set(items[0:4]) == {1, 3, 5, 7}
        assert set(items[4:7]) == {2, 4, 6}
        assert set(items[7:12]) == {9, 11, 13, 15, 17}
        assert items[12] == 8
        assert set(items[13:15]) == {19, 21}
        assert items[15] == 10

    # None key should do complete reshuffle and should break down the bucket boundaries
    _shuffle_items(items, key=None, preserve_bucket_order=True)
    assert (set(items[0:4]), set(items[4:7])) != ({1, 3, 5, 7}, {2, 4, 6})


def test_shuffles_buckets():
    # This is a cross-check to test shuffling of buckets.
    items = [
        1, 1,
        2, 2,
        3, 3,
        4, 4,
        5, 5,
        6, 6,
        7, 7,
        8, 8,
    ]
    items_copy = list(items)

    _shuffle_items(items, key=identity_key, preserve_bucket_order=False)

    assert items != items_copy

    # Items of the same bucket should remain next to each other.
    assert items[0] == items[1]
    assert items[2] == items[3]
    assert items[-1] == items[-2]
