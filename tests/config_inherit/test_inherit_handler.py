# -*- coding: utf-8 -*-

import pytest
from importlib import import_module
from lbdrabbit.config_inherit.inherit_handler import inherit_handler
from lbdrabbit.tests.auto_inherit_config import LbdFuncConfig
from lbdrabbit.apigw import HttpMethod


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


def test_inherit_handler():
    root_module_name = "lbdrabbit.tests.handlers"
    config_field = "__lbd_func_config__"

    inherit_handler(
        module_name=root_module_name,
        config_field=config_field,
        config_class=LbdFuncConfig,
        valid_func_name_list=HttpMethod.get_all_valid_func_name(),
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
