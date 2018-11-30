import functools
import os.path
from collections import OrderedDict

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
                for handler in session.random_order_bucket_type_key_handlers:
                    key = handler(item, key)

            return key

        bucket_type_keys[bucket_type] = wrapped
        return wrapped

    return decorator


@bucket_type_key('global')
def get_global_key(item):
    return None


@bucket_type_key('package')
def get_package_key(item):
    if not hasattr(item, "module"):
        return os.path.split(item.location[0])[0]
    return item.module.__package__


@bucket_type_key('module')
def get_module_key(item):
    return item.location[0]


@bucket_type_key('class')
def get_class_key(item):
    if not hasattr(item, "cls"):
        return item.location[0]
    if item.cls:
        return item.module.__name__, item.cls.__name__
    else:
        return item.module.__name__


@bucket_type_key('parent')
def get_parent_key(item):
    return item.parent


@bucket_type_key('grandparent')
def get_grandparent_key(item):
    return item.parent.parent


@bucket_type_key('none')
def get_none_key(item):
    raise RuntimeError('When shuffling is disabled (bucket_type=none), item key should not be calculated')


bucket_types = bucket_type_keys.keys()
