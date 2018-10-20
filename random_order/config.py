class Config:

    @classmethod
    def default_value(cls, value):
        return "default:" + str(value)

    def __init__(self, config):
        self._config = config

    @property
    def bucket_type(self):
        if not self.is_enabled:
            return 'none'
        else:
            return self._remove_default_prefix(self._config.getoption('random_order_bucket'))

    @property
    def is_enabled(self):
        return (
            self._config.getoption('random_order_enabled') or
            any(
                not self._config.getoption(name).startswith('default:')
                for name in ('random_order_bucket', 'random_order_seed')
            )
        )

    @property
    def seed(self):
        return self._remove_default_prefix(self._config.getoption('random_order_seed'))

    def _remove_default_prefix(self, value):
        if value.startswith('default:'):
            return value[len('default:'):]
        return value
