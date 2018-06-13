try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
import functools

bucket_type_keys = OrderedDict()


def bucket_type_key(bucket_type):
    """
    Registers a function that calculates test item key for the specified bucket type.
    """

    def decorator(f):

        @functools.wraps(f)
        def wrapped(item, session):
            key = f(item)

            if session is not None:
                for handler in session.pytest_random_order_bucket_type_key_handlers:
                    key = handler(item, key)

            return key

        bucket_type_keys[bucket_type] = wrapped
        return wrapped

    return decorator


@bucket_type_key('global')
def get_key(item):
    return None


@bucket_type_key('package')
def get_key(item):
    return item.module.__package__


@bucket_type_key('module')
def get_key(item):
    return item.module.__name__


@bucket_type_key('class')
def get_key(item):
    if item.cls:
        return item.module.__name__, item.cls.__name__
    else:
        return item.module.__name__


@bucket_type_key('parent')
def get_key(item):
    return item.parent


@bucket_type_key('grandparent')
def get_key(item):
    return item.parent.parent


@bucket_type_key('none')
def get_key(item):
    raise RuntimeError('When shuffling is disabled (bucket_type=none), item key should not be calculated')


bucket_types = bucket_type_keys.keys()
