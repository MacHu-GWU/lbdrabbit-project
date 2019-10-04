# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
from lbdrabbit.const import VALID_LBD_HANDLER_FUNC_NAME_LIST, DEFAULT_LBD_HANDLER_FUNC_NAME
from lbdrabbit.config_inherit.base import config_inherit_handler
from lbdrabbit.config_inherit.lbd_func_config import (
    LbdFuncConfig,
    DEFAULT_LBD_FUNC_CONFIG_FIELD,
    lbd_func_config_value_handler,
    template_creation_handler,
)
from lbdrabbit.example.cf import template

module_name = "lbdrabbit.example.handlers"
config_inherit_handler(
    module_name=module_name,
    config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
    config_class=LbdFuncConfig,
    valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
)

lbd_func_config_value_handler(
    module_name=module_name,
    config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
    config_class=LbdFuncConfig,
    valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
    default_lbd_handler_name=DEFAULT_LBD_HANDLER_FUNC_NAME,
)

template_creation_handler(
    module_name=module_name,
    config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
    config_class=LbdFuncConfig,
    valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
    template=template,
)

template.to_file("master.json")
