# -*- coding: utf-8 -*-

import pytest
import attr
from lbdrabbit.config_inherit.base import BaseConfig, REQUIRED, NOTHING


@attr.s
class LbdFuncConfig(BaseConfig):
    memory = attr.ib(default=REQUIRED)
    timeout = attr.ib(default=REQUIRED)
    alias = attr.ib(default=NOTHING)
    info = attr.ib(default=NOTHING)

    _default = {
        "memory": 128,
        "timeout": 3,
    }

    def post_init_hooker(self):
        self.info = "memory = {}, timeout = {}, alias = {}".format(
            self.memory, self.timeout, self.alias
        )


class TestBaseConfig(object):
    def test_absorb(self):
        c1 = LbdFuncConfig(
            memory=1024,
        )
        c2 = LbdFuncConfig(
            timeout=120,
        )

        assert c2.memory != 1024
        assert c2.timeout == 120
        c2.absorb(c1)
        assert c2.memory == 1024
        assert c2.timeout == 120

        assert c2.memory == 1024
        assert c1.timeout != 120
        c1.absorb(c2)
        assert c2.memory == 1024
        assert c1.timeout == 120

    def test_fill_na_with_default(self):
        c = LbdFuncConfig(
            memory=1024,
        )

        assert c.memory == 1024
        assert c.timeout != 3
        c.fill_na_with_default()
        assert c.memory == 1024
        assert c.timeout == 3

    def test_post_init_hooker(self):
        c = LbdFuncConfig(alias="my-func")
        assert c.info is NOTHING
        c.post_init_hooker()
        assert isinstance(c.info, str)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
