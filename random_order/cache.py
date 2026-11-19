"""
This module is called "cache" because it builds on the "cache" plugin:

    https://docs.pytest.org/en/latest/cache.html

"""

FAILED_FIRST_LAST_FAILED_BUCKET_KEY = "<failed_first_last_failed>"


def process_failed_first_last_failed(session, config, items):
    if not hasattr(config, "cache"):
        return

    if not config.getoption("failedfirst"):
        return

    last_failed_raw = config.cache.get("cache/lastfailed", None)
    if not last_failed_raw:
        return

    def assign_last_failed_to_same_bucket(item, key):
        if item.nodeid in last_failed_raw:
            return FAILED_FIRST_LAST_FAILED_BUCKET_KEY
        else:
            return key

    session.random_order_bucket_type_key_handlers.append(assign_last_failed_to_same_bucket)
