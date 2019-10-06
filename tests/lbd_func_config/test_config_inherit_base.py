# -*- coding: utf-8 -*-

import pytest
import attr
from importlib import import_module
from lbdrabbit.lbd_func_config.base import BaseConfig, REQUIRED, NOTHING, config_inherit_handler
from lbdrabbit.const import VALID_LBD_HANDLER_FUNC_NAME_LIST


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


def access_value(path):
    """
    helper method to access value of a field in LbdFuncConfig
    """
    parts = path.split(".")
    key = parts[-1]
    config_field = parts[-2]
    try:
        return getattr(
            getattr(
                import_module(".".join(parts[:-2])),
                config_field
            ),
            key
        )
    except:
        return getattr(
            getattr(
                getattr(
                    import_module(".".join(parts[:-3])),
                    parts[-3]
                ),
                config_field
            ),
            key
        )


def test_config_inherit_handler():
    root_module_name = "lbdrabbit.tests.handlers"
    config_field = "__lbd_func_config__"

    config_inherit_handler(
        module_name=root_module_name,
        config_field=config_field,
        config_class=LbdFuncConfig,
        valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
    )

    assert access_value(f"{root_module_name}.{config_field}.memory") == 128
    assert access_value(f"{root_module_name}.{config_field}.timeout") == 3
    assert access_value(f"{root_module_name}.{config_field}.alias") == "root"

    assert access_value(f"{root_module_name}.rest.users.{config_field}.timeout") == 30

    assert access_value(f"{root_module_name}.rest.users.get.{config_field}.timeout") == 30
    assert access_value(f"{root_module_name}.rest.users.get.{config_field}.alias") == "rest.users.get"

    assert access_value(f"{root_module_name}.rest.users.post.{config_field}.timeout") == 60
    assert access_value(f"{root_module_name}.rest.users.post.{config_field}.alias") == "rest.users.post"

    assert access_value(f"{root_module_name}.rest.users.any_.{config_field}.alias") == "users"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
