# -*- coding: utf-8 -*-

import random

import pytest


def pytest_addoption(parser):
    group = parser.getgroup('random-order')
    # group.addoption(
    #     '--random-order-seed',
    #     action='store',
    #     type=int,
    #     dest='random_order_seed',
    #     default=None,
    #     help='Seed value to reproduce a particular order',
    # )
    group.addoption(
        '--random-order-mode',
        action='store',
        dest='random_order_mode',
        default='module',
        choices=('global', 'package', 'module'),
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
}


def pytest_collection_modifyitems(session, config, items):
    sections = []

    # One of: global, package, module
    shuffle_mode = config.getoption('random_order_mode')

    item_key = _random_order_item_keys[shuffle_mode]

    # Mark the beginning and ending of each key's test items in the items collection
    # so we know the boundaries of reshuffle.
    for i, item in enumerate(items):
        key = item_key(item)
        if not sections:
            assert i == 0
            sections.append([key, i, None])
        elif sections[-1][0] != key:
            sections[-1][2] = i
            sections.append([key, i, None])

    if sections:
        sections[-1][2] = len(items)

    for key, i, j in sections:
        key_items = items[i:j]
        random.shuffle(key_items)
        items[i:j] = key_items
