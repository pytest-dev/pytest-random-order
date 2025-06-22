import random
import sys
import traceback
import warnings

import pytest

from random_order.bucket_types import bucket_type_keys, bucket_types
from random_order.cache import process_failed_first_last_failed
from random_order.config import Config
from random_order.shuffler import _disable, _get_set_of_item_ids, _shuffle_items
from random_order.xdist import XdistHooks


def pytest_addoption(parser):
    group = parser.getgroup("pytest-random-order options")
    group.addoption(
        "--random-order",
        action="store_true",
        dest="random_order_enabled",
        help="Randomise test order (by default, it is disabled) with default configuration.",
    )
    group.addoption(
        "--random-order-bucket",
        action="store",
        dest="random_order_bucket",
        default=Config.default_value("module"),
        choices=bucket_types,
        help="Randomise test order within specified test buckets.",
    )
    group.addoption(
        "--random-order-seed",
        action="store",
        dest="random_order_seed",
        default=Config.default_value(str(random.randint(1, 1000000))),
        help="Randomise test order using a specific seed.",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "random_order(disabled=True): disable reordering of tests within a module or class"
    )

    if config.pluginmanager.hasplugin("xdist"):
        config.pluginmanager.register(XdistHooks())

    if hasattr(config, "workerinput"):
        # pytest-xdist: use seed generated on main.
        seed = config.workerinput["random_order_seed"]
        if hasattr(config, "cache"):
            assert config.cache is not None
            config.cache.set("random_order_seed", seed)
        config.option.random_order_seed = seed


def pytest_report_header(config):
    plugin = Config(config)
    if not plugin.is_enabled:
        return "Test order randomisation NOT enabled. Enable with --random-order or --random-order-bucket=<bucket_type>"
    return ("Using --random-order-bucket={plugin.bucket_type}\n" "Using --random-order-seed={plugin.seed}\n").format(
        plugin=plugin
    )


def pytest_collection_modifyitems(session, config, items):
    failure = None

    session.random_order_bucket_type_key_handlers = []
    process_failed_first_last_failed(session, config, items)

    item_ids = _get_set_of_item_ids(items)

    plugin = Config(config)

    try:
        seed = plugin.seed
        bucket_type = plugin.bucket_type
        if bucket_type != "none":
            _shuffle_items(
                items,
                bucket_key=bucket_type_keys[bucket_type],
                disable=_disable,
                seed=seed,
                session=session,
            )

    except Exception as e:
        # See the finally block -- we only fail if we have lost user's tests.
        _, _, exc_tb = sys.exc_info()
        failure = "pytest-random-order plugin has failed with {0!r}:\n{1}".format(
            e, "".join(traceback.format_tb(exc_tb, 10))
        )
        if not hasattr(pytest, "PytestWarning"):
            config.warn(0, failure, None)
        else:
            warnings.warn(pytest.PytestWarning(failure))

    finally:
        # Fail only if we have lost user's tests
        if item_ids != _get_set_of_item_ids(items):
            if not failure:
                failure = "pytest-random-order plugin has failed miserably"
            raise RuntimeError(failure)
