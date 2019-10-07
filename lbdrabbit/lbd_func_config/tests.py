# -*- coding: utf-8 -*-

"""
A test config instance with _py_module and _py_function. So we can easily
use this to create a deep copy of a new instance and do testing.
"""

import attr
from importlib import import_module
from .lbd_func_config import LbdFuncConfig


def handler(event, context): pass


__lbd_func_config__ = LbdFuncConfig()
__lbd_func_config__._root_module_name = "lbdrabbit"
__lbd_func_config__._py_module = import_module(handler.__module__)
__lbd_func_config__._py_function = handler


def new_conf_inst() -> LbdFuncConfig:
    return attr.evolve(__lbd_func_config__)
