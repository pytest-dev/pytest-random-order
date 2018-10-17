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


def get_genid(item):
    genid = item._genid
    if genid and '-' in genid:
        genid = genid.split('-', 1)[1]
    return genid


@bucket_type_key('global')
def get_global_key(item):
    return None, get_genid(item)


@bucket_type_key('package')
def get_package_key(item):
    return item.module.__package__, get_genid(item)


@bucket_type_key('module')
def get_module_key(item):
    return item.module.__name__, get_genid(item)


@bucket_type_key('class')
def get_class_key(item):
    if item.cls:
        return item.module.__name__, item.cls.__name__, get_genid(item)
    else:
        return item.module.__name__, get_genid(item)


@bucket_type_key('parent')
def get_parent_key(item):
    return item.parent, get_genid(item)


@bucket_type_key('grandparent')
def get_grandparent_key(item):
    return item.parent.parent, get_genid(item)


@bucket_type_key('none')
def get_none_key(item):
    raise RuntimeError('When shuffling is disabled (bucket_type=none), item key should not be calculated')


bucket_types = bucket_type_keys.keys()
