import pytest


class XdistHooks:

    def pytest_configure_node(self, node: pytest.Item) -> None:
        seed = node.config.getoption('random_order_seed')
        node.workerinput['random_order_seed'] = seed
