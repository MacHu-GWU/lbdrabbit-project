# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
from lbdrabbit.const import VALID_LBD_HANDLER_FUNC_NAME_LIST, DEFAULT_LBD_HANDLER_FUNC_NAME
from lbdrabbit.config_inherit.base import config_inherit_handler
from lbdrabbit.config_inherit.lbd_func_config import (
    LbdFuncConfig,
    DEFAULT_LBD_FUNC_CONFIG_FIELD,
    config_derivable_handler,
)


def test_config_derivable_handler():
    module_name = "lbdrabbit.example.handlers"
    config_inherit_handler(
        module_name=module_name,
        config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
        config_class=LbdFuncConfig,
        valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
    )

    config_derivable_handler(
        module_name=module_name,
        config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
        config_class=LbdFuncConfig,
        valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
        default_lbd_handler_name=DEFAULT_LBD_HANDLER_FUNC_NAME,
    )


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
